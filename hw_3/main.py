import asyncio
import time

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI(
    title="Homework 3",
    description="This is a FastAPI application for Homework 3.",
    version="1.0.0",
)


class CalculateRequest(BaseModel):
    numbers: list[float]
    delays: list[float]


class SquareResult(BaseModel):
    number: float
    square: float
    delay: float
    time: float


class CalculateResponse(BaseModel):
    results: list[SquareResult]
    total_time: float
    parallel_faster_than_sequential: bool


async def square(number: float, delay: float) -> SquareResult:
    start = time.perf_counter()
    await asyncio.sleep(delay)

    return SquareResult(
        number=number,
        square=number**2,
        delay=delay,
        time=round(time.perf_counter() - start, 3),
    )


@app.post("/calculate/", response_model=CalculateResponse)
async def calculate(data: CalculateRequest) -> CalculateResponse:
    if len(data.numbers) != len(data.delays):
        raise HTTPException(
            status_code=422,
            detail="Списки numbers и delays должны быть одинаковой длины.",
        )
    if any(delay < 0 for delay in data.delays):
        raise HTTPException(
            status_code=422, detail="Задержки не могут быть отрицательными."
        )

    start = time.perf_counter()
    results = await asyncio.gather(
        *(
            square(number, delay)
            for number, delay in zip(data.numbers, data.delays, strict=True)
        )
    )
    total_time = time.perf_counter() - start
    expected_sequential_time = sum(data.delays)

    return CalculateResponse(
        results=results,
        total_time=round(total_time, 3),
        parallel_faster_than_sequential=total_time < expected_sequential_time,
    )
