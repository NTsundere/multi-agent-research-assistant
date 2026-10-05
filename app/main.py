import time
from fastapi import FastAPI, HTTPException
from fastapi.concurrency import run_in_threadpool
from app.schemas import ResearchRequest, ResearchResponse
from app.graph.graph import graph
from app.config import settings
from app.logger import setup_logger

logger = setup_logger(__name__)

app = FastAPI(
    title="Multi-Agent Research Assistant",
    description="Supervisor + Researcher + Analyst + Writer on LangGraph",
    version="1.0.0",
)


@app.get("/health")
async def health():
    return {"status": "healthy", "model": settings.ollama_model}


def _run_graph(query: str, thread_id: str):
    config = {"configurable": {"thread_id": thread_id}}
    return graph.invoke(
        {
            "messages": [{"role": "user", "content": query}],
            "research_notes": "",
            "analysis": "",
            "final_report": "",
        },
        config=config,
    )


@app.post("/research", response_model=ResearchResponse)
async def research(req: ResearchRequest):
    start = time.perf_counter()
    try:
        result = await run_in_threadpool(_run_graph, req.query, req.thread_id)
        latency = (time.perf_counter() - start) * 1000
        logger.info(f"Research done in {latency:.0f}ms | thread={req.thread_id}")

        final_report = result.get("final_report", "").strip()
        if not final_report:
            final_report = result.get("analysis", "").strip() or result.get("research_notes", "").strip()

        return ResearchResponse(
            final_report=final_report,
            research_notes=result.get("research_notes", ""),
            analysis=result.get("analysis", ""),
            thread_id=req.thread_id,
        )
    except Exception as e:
        logger.error(f"Research failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000)