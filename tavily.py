import json
import logging
import os
from typing import Any, Dict

import requests
from fastapi import HTTPException
from dotenv import load_dotenv

load_dotenv()

class TavilyClient:
    def __init__(self):
        self.api_key = os.getenv("TAVILY_API_KEY")
        if not self.api_key:
            raise ValueError("TAVILY_API_KEY가 설정되지 않았습니다.")
        self.base_url = "https://api.tavily.com"

    def get_web_search_data(
            self,
            query: str,
            params: Dict[str, Any]
    ):
        """
        참조 데이터를 검색합니다.
        Args:
            query: 사용자 질문 (예: 애플 최근 20일 종가)
            params: API Parameters
        """

        endpoint = f"{self.base_url}/search"
        params = {
            "api_key": self.api_key,
            "query": query,
            "days": params["days"],
            "topic": params["topic"],
            "max_results": params["max_results"],
            "search_depth": params["search_depth"],
            "include_answer": params["include_answer"],
            "include_images": params["include_images"],
            "include_image_descriptions": params["include_image_description"],
            "include_raw_content": params["include_raw_content"],
            "include_domains": params["include_domains"],
            "exclude_domains": params["exclude_domains"]
        }

        logging.info(f"TAVILY API 요청 \n{endpoint} with params {params}")
        response = requests.post(url=endpoint, json=params)

        if response.status_code != 200:
            logging.error(f"TAVILY API 오류 응답 \n{response.status_code} - {response.text}")
            raise HTTPException(
                status_code=response.status_code,
                detail=f"TAVILY API 오류: {response.text}"
            )

        data = response.json()
        logging.info(f"TAVILY API 응답\n{json.dumps(data, indent=4, ensure_ascii=False)}")

        if "results" not in data:
            logging.error("유효하지 않은 응답 데이터입니다.")
            raise HTTPException(
                status_code=400,
                detail="유효하지 않은 응답 데이터입니다."
            )

        web_search_data = [
            {
                'url': item['url'],
                'title': item['title'],
                'content': item['content'],
                'score': item['score']
            }
            for item in data.get("results")
        ]

        return web_search_data