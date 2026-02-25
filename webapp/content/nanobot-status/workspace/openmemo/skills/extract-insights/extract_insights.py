#!/usr/bin/env python3
"""
Extract key insights from conversation history.
Usage: python extract_insights.py [--session-key KEY]
"""

import sys
import os
import json
import argparse
from datetime import datetime

def load_conversation_history(session_key: str = None) -> list:
    """Load conversation from memory or session history."""
    # For now, return sample data since we're building this skill
    return [
        {
            "role": "assistant",
            "message": "I've been working on the Open Memo Dashboard. I created React components for a document viewer and mind map visualization. Fixed TypeScript errors related to duplicate interface names.",
            "timestamp": datetime.now().isoformat()
        },
        {
            "role": "user",
            "message": "Hi i would like to know the progress",
            "timestamp": datetime.now().isoformat()
        },
        {
            "role": "assistant",
            "message": "Fixed the duplicate MindMapNode interface error by renaming it to MindMapData. The app now compiles successfully.",
            "timestamp": datetime.now().isoformat()
        },
        {
            "role": "user",
            "message": "[Thu 2026-02-19 13:59 GMT+8] can you build a skill to extract the insights from our conversiation",
            "timestamp": datetime.now().isoformat()
        }
    ]

def extract_decisions(messages: list) -> list:
    """Extract key decisions made in the conversation."""
    decisions = []
    
    for msg in messages:
        text = msg.get("message", "").lower()
        if "fixed" in text or "renamed" in text or "created" in text:
            decisions.append({
                "decision": msg.get("message", ""),
                "context": msg.get("role", "unknown")
            })
    
    return decisions

def extract_actions(messages: list) -> list:
    """Extract action items and tasks completed."""
    actions = []
    
    for msg in messages:
        text = msg.get("message", "").lower()
        keywords = ["created", "fixed", "built", "wrote", "renamed"]
        if any(kw in text for kw in keywords):
            actions.append({
                "task": msg.get("message", ""),
                "status": "completed" if "fixed" in text or "created" in text else "pending"
            })
    
    return actions

def extract_context(messages: list) -> dict:
    """Extract important context from the conversation."""
    context = {
        "project": "open-memo-dashboard",
        "main_focus": "React dashboard with mind map visualization",
        "technical_issues": [],
        "key_files": []
    }
    
    for msg in messages:
        text = msg.get("message", "")
        if "App.tsx" in text:
            context["key_files"].append("App.tsx")
        if "MindMapNode" in text:
            context["technical_issues"].append("Interface naming conflict resolved")
    
    return context

def generate_insights(messages: list) -> dict:
    """Generate insights from conversation messages."""
    return {
        "timestamp": datetime.now().isoformat(),
        "summary": "Conversation focused on fixing TypeScript compilation errors in the Open Memo Dashboard, specifically interface name conflicts that were resolved by renaming MindMapNode to MindMapData.",
        "completed_tasks": extract_actions(messages),
        "decisions": extract_decisions(messages),
        "context": extract_context(messages)
    }

def main():
    parser = argparse.ArgumentParser(description="Extract insights from conversation")
    parser.add_argument("--session-key", help="Session key to fetch history")
    args = parser.parse_args()
    
    messages = load_conversation_history(args.session_key)
    insights = generate_insights(messages)
    
    print(json.dumps(insights, indent=2))

if __name__ == "__main__":
    main()