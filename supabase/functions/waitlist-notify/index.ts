import "@supabase/functions-js/edge-runtime.d.ts";

const RESEND_API_KEY = Deno.env.get("RESEND_API_KEY")!;
const NOTIFY_EMAIL = "phil@onchainstudies.com";

Deno.serve(async (req) => {
  const payload = await req.json();
  const email = payload.record?.email;

  if (!email) {
    return new Response("No email in payload", { status: 400 });
  }

  const res = await fetch("https://api.resend.com/emails", {
    method: "POST",
    headers: {
      "Authorization": `Bearer ${RESEND_API_KEY}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      from: "Onchain Studies <onboarding@resend.dev>",
      to: [NOTIFY_EMAIL],
      subject: `New waitlist signup: ${email}`,
      text: `${email} just joined the Onchain Studies waitlist.`,
    }),
  });

  if (!res.ok) {
    const error = await res.text();
    return new Response(`Resend error: ${error}`, { status: 500 });
  }

  return new Response("OK", { status: 200 });
});
