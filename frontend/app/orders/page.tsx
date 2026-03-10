"use client"
import { useEffect, useState } from "react";
import axios from "axios";

export default function OrdersPage() {
  const [orders, setOrders] = useState([]);

  useEffect(() => {
    // Misol uchun localStorage orqali telegram_id olamiz
    const telegram_id = localStorage.getItem("telegram_id");
    if (!telegram_id) return;

    axios.get(`http://localhost:8000/orders/user/${telegram_id}`)
      .then(res => setOrders(res.data))
      .catch(err => console.error(err));
  }, []);

  return (
    <div className="p-6">
      <h2 className="text-2xl font-bold mb-4">Mening Buyurtmalarim</h2>
      <div className="flex flex-col gap-3">
        {orders.length === 0 && <p>Hech qanday buyurtma topilmadi</p>}
        {orders.map((o: any) => (
          <div key={o.id} className="border p-4 rounded bg-gray-800">
            <p>Order №: {o.order_number}</p>
            <p>Game ID: {o.player_id}</p>
            <p>Zona: {o.zone_id}</p>
            <p>Nick: {o.nickname}</p>
            <p>Diamond: {o.diamond}</p>
            <p>Price: {o.price}</p>
            <p>Status: {o.status}</p>
            {o.cancel_reason && <p>Bekor qilish sababi: {o.cancel_reason}</p>}
          </div>
        ))}
      </div>
    </div>
  )
}
