const API_BASE = import.meta.env.VITE_API_URL || "http://localhost:8000";

export const API_URL = API_BASE;

export async function api(path, method="GET", body) {
  const res = await fetch(API_BASE + path, {
    method,
    headers: {
      "Content-Type": "application/json",
      Authorization: "Bearer " + localStorage.token
    },
    body: body && JSON.stringify(body)
  });
  return res.json();
}
