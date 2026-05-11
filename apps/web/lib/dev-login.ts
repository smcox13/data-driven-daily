export function isDevLoginBypassEnabled() {
  return process.env.DEV_LOGIN_BYPASS === "true" || process.env.GOOGLE_CLIENT_ID === "dummy";
}

