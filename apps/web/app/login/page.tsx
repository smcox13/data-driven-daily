import Link from "next/link";

import { signIn } from "@/lib/auth";
import { isDevLoginBypassEnabled } from "@/lib/dev-login";

export default function LoginPage() {
  const devLoginBypassEnabled = isDevLoginBypassEnabled();

  return (
    <div className="flex min-h-[80vh] items-center justify-center">
      <div className="max-w-xl rounded-[32px] border border-white/70 bg-white/95 p-10 text-center shadow-panel">
        <p className="text-xs font-semibold uppercase tracking-[0.24em] text-brand">
          {devLoginBypassEnabled ? "Local Demo Access" : "Google Sign-In"}
        </p>
        <h2 className="mt-3 font-serif text-4xl text-ink">Editorial access stays simple in v1</h2>
        <p className="mt-4 text-sm leading-7 text-slate">
          The first release assumes one organization with Google OAuth for editors and admins. While local auth is still being
          stitched together, you can enter the app directly in demo mode and use the backend's seeded editor context.
        </p>
        <div className="mt-8 flex flex-col items-center gap-4">
          {devLoginBypassEnabled ? (
            <Link href="/" className="rounded-full bg-ink px-6 py-3 text-sm font-medium text-white">
              Enter Local Demo
            </Link>
          ) : null}
          <form
            action={async () => {
              "use server";
              await signIn("google", { redirectTo: "/" });
            }}
          >
            <button
              type="submit"
              className="rounded-full border border-slate-300 bg-white px-6 py-3 text-sm font-medium text-ink"
            >
              Continue with Google
            </button>
          </form>
        </div>
        {devLoginBypassEnabled ? (
          <p className="mt-5 text-xs leading-6 text-slate">
            Demo mode is enabled because `DEV_LOGIN_BYPASS=true` or dummy Google credentials are active in the dev server.
          </p>
        ) : null}
      </div>
    </div>
  );
}
