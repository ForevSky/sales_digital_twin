"""Pipeline 输入模型。"""

from pydantic import BaseModel, Field


class ProcessRequest(BaseModel):
    """单次处理的输入载体，由 CLI 构造后传入 Pipeline。"""

    text: str = Field(description="销售通话或会议转写文本")

