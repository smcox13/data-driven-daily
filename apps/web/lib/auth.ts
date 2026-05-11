import NextAuth from "next-auth";
import Google from "next-auth/providers/google";

import { isDevLoginBypassEnabled } from "@/lib/dev-login";

export const { handlers, auth, signIn, signOut } = NextAuth({
  providers: [
    Google({
      clientId: process.env.GOOGLE_CLIENT_ID ?? "",
      clientSecret: process.env.GOOGLE_CLIENT_SECRET ?? ""
    })
  ],
  pages: {
    signIn: "/login"
  },
  session: {
    strategy: "jwt"
  },
  callbacks: {
    authorized({ auth: activeSession, request }) {
      if (isDevLoginBypassEnabled()) {
        return true;
      }
      if (request.nextUrl.pathname.startsWith("/login")) {
        return true;
      }
      return Boolean(activeSession);
    },
    async jwt({ token }) {
      const mutableToken = token as typeof token & { role?: string; orgSlug?: string };
      mutableToken.role = mutableToken.role ?? "editor";
      mutableToken.orgSlug = mutableToken.orgSlug ?? process.env.DEFAULT_ORG_SLUG ?? "data-driven-daily";
      return token;
    },
    async session({ session, token }) {
      if (session.user) {
        const mutableSession = session as typeof session & {
          user: {
            name?: string | null;
            email?: string | null;
            image?: string | null;
            role?: string;
            orgSlug?: string;
          };
        };
        const mutableToken = token as typeof token & { role?: string; orgSlug?: string };
        mutableSession.user.role = typeof mutableToken.role === "string" ? mutableToken.role : "editor";
        mutableSession.user.orgSlug = typeof mutableToken.orgSlug === "string" ? mutableToken.orgSlug : "data-driven-daily";
      }
      return session;
    }
  }
});

declare module "next-auth" {
  interface Session {
    user?: {
      name?: string | null;
      email?: string | null;
      image?: string | null;
      role?: string;
      orgSlug?: string;
    };
  }
}
