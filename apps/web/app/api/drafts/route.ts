import { NextResponse } from "next/server";

import { backendJson, BackendRequestError } from "@/lib/backend-api";

export async function POST(request: Request) {
  try {
    const payload = await request.json();
    const draft = await backendJson("/drafts/generate", {
      method: "POST",
      body: JSON.stringify(payload)
    });
    return NextResponse.json(draft, { status: 201 });
  } catch (error) {
    if (error instanceof BackendRequestError) {
      return NextResponse.json({ detail: error.message }, { status: error.status });
    }
    return NextResponse.json({ detail: "Unable to generate draft" }, { status: 500 });
  }
}

