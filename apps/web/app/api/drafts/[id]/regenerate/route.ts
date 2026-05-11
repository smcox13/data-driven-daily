import { NextResponse } from "next/server";

import { backendJson, BackendRequestError } from "@/lib/backend-api";

export async function POST(request: Request, { params }: { params: Promise<{ id: string }> }) {
  try {
    const { id } = await params;
    const payload = await request.json();
    const draft = await backendJson(`/drafts/${id}/regenerate`, {
      method: "POST",
      body: JSON.stringify(payload)
    });
    return NextResponse.json(draft);
  } catch (error) {
    if (error instanceof BackendRequestError) {
      return NextResponse.json({ detail: error.message }, { status: error.status });
    }
    return NextResponse.json({ detail: "Unable to regenerate draft content" }, { status: 500 });
  }
}

