"""
LLMサービス
自然言語処理、パターン解析
"""
import json
from typing import Dict, Any

from openai import AsyncOpenAI
from app.config import get_settings

settings = get_settings()


class LLMService:
    """LLM連携サービス"""
    
    def __init__(self):
        self.provider = settings.LLM_PROVIDER
        
        if self.provider == "openai":
            self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
            self.model = "gpt-4o-mini"
        elif self.provider == "openrouter":
            self.client = AsyncOpenAI(
                api_key=settings.OPENROUTER_API_KEY,
                base_url="https://openrouter.ai/api/v1"
            )
            self.model = "openai/gpt-4o-mini"
        else:
            raise ValueError(f"Unsupported LLM provider: {self.provider}")
    
    async def parse_pattern(self, user_input: str) -> Dict[str, Any]:
        """
        自然言語から投資パターンを解析
        """
        system_prompt = """
        あなたは投資パターン解析のエキスパートです。
        ユーザーの自然言語入力から、構造化された投資条件を抽出してください。
        
        以下のJSON形式で出力してください：
        {
            "strategy": "戦略タイプ (dividend_focus|growth|value|technical|hybrid)",
            "filters": {
                "per_min": float or null,
                "per_max": float or null,
                "pbr_min": float or null,
                "pbr_max": float or null,
                "dividend_yield_min": float or null,
                "dividend_yield_max": float or null,
                "market_cap_min": int or null,
                "market_cap_max": int or null,
                "price_change_min": float or null,
                "price_change_max": float or null
            },
            "sectors": ["業種1", "業種2"],  // 言及された業種・セクター
            "sort_by": "per|pbr|dividend_yield|market_cap|price_change",
            "sort_order": "asc|desc",
            "keywords": [抽出したキーワード]
        }
        
        ルール：
        - 数値は必ず数値型で出力（文字列ではない）
        - 単位は削除（"倍"、"%"、"円"など）
        - 不明な条件はnull
        - "銀行株"、"銀行セクター"などと言及された場合、sectorsに"銀行"を追加
        - "製薬"、"医薬品"、"バイオ"などと言及された場合、sectorsに"医薬品"を追加
        - "IT"、"テクノロジー"、"半導体"などと言及された場合、sectorsに"電気機器"を追加
        - "食品"、"飲料"などと言及された場合、sectorsに"食料品"を追加
        - "商社"、"卸売"などと言及された場合、sectorsに"卸売"を追加
        """
        
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_input}
                ],
                temperature=0.1,
                response_format={"type": "json_object"}
            )
            
            content = response.choices[0].message.content
            parsed = json.loads(content)
            
            # デフォルト値設定
            parsed.setdefault("strategy", "hybrid")
            parsed.setdefault("filters", {})
            parsed.setdefault("sort_by", "dividend_yield")
            parsed.setdefault("sort_order", "desc")
            parsed.setdefault("keywords", [])
            
            return parsed
            
        except Exception as e:
            print(f"LLM parsing error: {e}")
            # フォールバック：シンプルなルールベース解析
            return self._fallback_parse(user_input)
    
    def _fallback_parse(self, user_input: str) -> Dict[str, Any]:
        """LLM失敗時のフォールバック解析"""
        filters = {}
        keywords = []
        sectors = []
        
        # 簡易的なキーワード抽出
        text = user_input.lower()
        
        # PER抽出
        if "per" in text:
            import re
            per_matches = re.findall(r'per[=＝](\d+)[倍]?', text)
            if per_matches:
                filters["per_max"] = int(per_matches[0])
                keywords.append("PER")
        
        # 配当利回り抽出
        if "配当" in user_input or "dividend" in text:
            import re
            div_matches = re.findall(r'(\d+)[%％]', user_input)
            if div_matches:
                filters["dividend_yield_min"] = int(div_matches[0])
                keywords.append("高配当")
        
        # セクター抽出
        if any(word in user_input for word in ["銀行", "金融", "銀行株"]):
            sectors.append("銀行")
            keywords.append("銀行")
        if any(word in user_input for word in ["医薬品", "製薬", "バイオ", "薬"]):
            sectors.append("医薬品")
            keywords.append("医薬品")
        if any(word in user_input for word in ["IT", "テクノロジー", "半導体", "電子", "電機"]):
            sectors.append("電気機器")
            keywords.append("電気機器")
        if any(word in user_input for word in ["食品", "飲料", "食料"]):
            sectors.append("食料品")
            keywords.append("食料品")
        if any(word in user_input for word in ["商社", "卸売", "貿易"]):
            sectors.append("卸売")
            keywords.append("商社")
        if any(word in user_input for word in ["鉄道", "交通", "運輸"]):
            sectors.append("鉄道・バス")
            keywords.append("鉄道")
        if any(word in user_input for word in ["保険", "生保", "損保"]):
            sectors.append("保険")
            keywords.append("保険")
        if any(word in user_input for word in ["自動車", "車", "トヨタ", "ホンダ"]):
            sectors.append("輸送用機器")
            keywords.append("自動車")
        
        # 戦略判定
        strategy = "hybrid"
        if "配当" in user_input:
            strategy = "dividend_focus"
        elif "成長" in user_input or "グロース" in user_input:
            strategy = "growth"
        elif "割安" in user_input or "バリュー" in user_input:
            strategy = "value"
        
        return {
            "strategy": strategy,
            "filters": filters,
            "sectors": sectors,
            "sort_by": "dividend_yield" if strategy == "dividend_focus" else "per",
            "sort_order": "asc" if strategy == "value" else "desc",
            "keywords": keywords
        }
    
    async def generate_recommendation_reason(
        self,
        pattern_name: str,
        pattern_filters: Dict,
        stock_data: Dict
    ) -> str:
        """
        レコメンド理由を生成
        """
        prompt = f"""
        ユーザーに対して、なぜこの銘柄が推奨されるかを説明してください。
        
        パターン: {pattern_name}
        パターンフィルタ: {json.dumps(pattern_filters, ensure_ascii=False)}
        
        銘柄情報:
        - コード: {stock_data.get('code')}
        - 名前: {stock_data.get('name')}
        - 現在価格: {stock_data.get('price')}円
        - PER: {stock_data.get('per')}
        - PBR: {stock_data.get('pbr')}
        - 配当利回り: {stock_data.get('dividend_yield')}%
        
        マッチングスコア: {stock_data.get('match_score', 0)}
        
        3-4文程度の簡潔な説明を日本語で生成してください。
        """
        
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=200
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            print(f"LLM generation error: {e}")
            return f"{stock_data.get('name')}はあなたの「{pattern_name}」パターンに適合しています。"
