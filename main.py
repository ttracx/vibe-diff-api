"""
vibe-diff-api - Text and JSON comparison API
"""
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from difflib import unified_diff, SequenceMatcher
import json
from typing import Any

app = FastAPI(
    title="vibe-diff-api",
    description="Compare texts, JSON objects, and calculate similarity",
    version="1.0.0"
)


class TextDiffRequest(BaseModel):
    text1: str
    text2: str
    context_lines: int = 3


class TextDiffResponse(BaseModel):
    diff: list[str]
    has_changes: bool
    additions: int
    deletions: int


class JsonDiffRequest(BaseModel):
    json1: Any
    json2: Any


class JsonDiffItem(BaseModel):
    path: str
    type: str  # "added", "removed", "changed"
    old_value: Any = None
    new_value: Any = None


class JsonDiffResponse(BaseModel):
    differences: list[JsonDiffItem]
    has_changes: bool
    total_changes: int


class SimilarityRequest(BaseModel):
    text1: str
    text2: str


class SimilarityResponse(BaseModel):
    similarity_percent: float
    matching_blocks: int
    text1_length: int
    text2_length: int


def deep_diff(obj1: Any, obj2: Any, path: str = "") -> list[JsonDiffItem]:
    """Recursively compare two JSON objects and return differences."""
    differences = []
    
    if type(obj1) != type(obj2):
        differences.append(JsonDiffItem(
            path=path or "root",
            type="changed",
            old_value=obj1,
            new_value=obj2
        ))
        return differences
    
    if isinstance(obj1, dict):
        all_keys = set(obj1.keys()) | set(obj2.keys())
        for key in all_keys:
            new_path = f"{path}.{key}" if path else key
            if key not in obj1:
                differences.append(JsonDiffItem(
                    path=new_path,
                    type="added",
                    new_value=obj2[key]
                ))
            elif key not in obj2:
                differences.append(JsonDiffItem(
                    path=new_path,
                    type="removed",
                    old_value=obj1[key]
                ))
            else:
                differences.extend(deep_diff(obj1[key], obj2[key], new_path))
    
    elif isinstance(obj1, list):
        max_len = max(len(obj1), len(obj2))
        for i in range(max_len):
            new_path = f"{path}[{i}]"
            if i >= len(obj1):
                differences.append(JsonDiffItem(
                    path=new_path,
                    type="added",
                    new_value=obj2[i]
                ))
            elif i >= len(obj2):
                differences.append(JsonDiffItem(
                    path=new_path,
                    type="removed",
                    old_value=obj1[i]
                ))
            else:
                differences.extend(deep_diff(obj1[i], obj2[i], new_path))
    
    else:
        if obj1 != obj2:
            differences.append(JsonDiffItem(
                path=path or "root",
                type="changed",
                old_value=obj1,
                new_value=obj2
            ))
    
    return differences


@app.get("/")
async def root():
    return {
        "name": "vibe-diff-api",
        "version": "1.0.0",
        "endpoints": [
            "POST /diff - Compare two texts",
            "POST /json-diff - Compare two JSON objects",
            "POST /similarity - Calculate text similarity"
        ]
    }


@app.get("/health")
async def health():
    return {"status": "healthy"}


@app.post("/diff", response_model=TextDiffResponse)
async def text_diff(request: TextDiffRequest):
    """Compare two texts and return unified diff."""
    lines1 = request.text1.splitlines(keepends=True)
    lines2 = request.text2.splitlines(keepends=True)
    
    diff = list(unified_diff(
        lines1, lines2,
        fromfile="text1",
        tofile="text2",
        n=request.context_lines
    ))
    
    additions = sum(1 for line in diff if line.startswith('+') and not line.startswith('+++'))
    deletions = sum(1 for line in diff if line.startswith('-') and not line.startswith('---'))
    
    return TextDiffResponse(
        diff=diff,
        has_changes=len(diff) > 0,
        additions=additions,
        deletions=deletions
    )


@app.post("/json-diff", response_model=JsonDiffResponse)
async def json_diff(request: JsonDiffRequest):
    """Compare two JSON objects and return structural differences."""
    try:
        differences = deep_diff(request.json1, request.json2)
        return JsonDiffResponse(
            differences=differences,
            has_changes=len(differences) > 0,
            total_changes=len(differences)
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error comparing JSON: {str(e)}")


@app.post("/similarity", response_model=SimilarityResponse)
async def text_similarity(request: SimilarityRequest):
    """Calculate similarity percentage between two texts."""
    matcher = SequenceMatcher(None, request.text1, request.text2)
    similarity = matcher.ratio() * 100
    matching_blocks = len(matcher.get_matching_blocks()) - 1  # Exclude empty final block
    
    return SimilarityResponse(
        similarity_percent=round(similarity, 2),
        matching_blocks=max(0, matching_blocks),
        text1_length=len(request.text1),
        text2_length=len(request.text2)
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
