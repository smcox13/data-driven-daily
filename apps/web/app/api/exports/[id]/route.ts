import { NextResponse } from "next/server";

import { backendJson, BackendRequestError } from "@/lib/backend-api";

export async function POST(_request: Request, { params }: { params: Promise<{ id: string }> }) {
  try {
    const { id } = await params;
    const payload = await backendJson(`/exports/${id}`, {
      method: "POST"
    });
    return NextResponse.json(payload, { status: 201 });
  } catch (error) {
    if (error instanceof BackendRequestError) {
      return NextResponse.json({ detail: error.message }, { status: error.status });
    }
    return NextResponse.json({ detail: "Unable to export draft" }, { status: 500 });
  }
}
