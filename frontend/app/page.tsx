"use client"
import { useState } from "react";
import axios from "axios";
import Link from "next/link";

export default function Home() {
  const [username, setUsername] = useState("");
  const [telegramId, setTelegramId] = useState("");

  const register = async () => {
    if (!telegramId) return alert("Telegram ID kiriting");
    const res = await axios.post("http://localhost:8000/auth/register", {
      telegram_id: telegramId,
      username
    });
    alert("Ro'yhatdan o'tish: " + res.data.status);
  }

  return (
    <div className="flex flex-col items-center justify-center min-h-screen gap-6">
      <h1 className="text-4xl font-bold">MLBB TopUp</h1>

      <input
        type="text"
        placeholder="Telegram username"
        value={username}
        onChange={(e) => setUsername(e.target.value)}
        className="p-2 rounded bg-gray-800 w-80"
      />
      <input
        type="text"
        placeholder="Telegram ID"
        value={telegramId}
        onChange={(e) => setTelegramId(e.target.value)}
        className="p-2 rounded bg-gray-800 w-80"
      />
      <button
        onClick={register}
        className="bg-blue-600 px-4 py-2 rounded font-bold hover:bg-blue-700"
      >
        Ro'yhatdan o'tish
      </button>

      <div className="flex gap-4 mt-4">
        <Link href="/orders" className="underline hover:text-blue-400">Buyurtmalarim</Link>
        <Link href="/admin" className="underline hover:text-red-400">Admin panel</Link>
      </div>
    </div>
  )
}
