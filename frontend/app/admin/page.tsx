"use client"
import { useEffect, useState } from "react";
import axios from "axios";

export default function AdminPage() {
  const [orders, setOrders] = useState([]);
  const [reason, setReason] = useState("");

  useEffect(() => {
    axios.get("http://localhost:8000/orders")
      .then(res => setOrders(res.data))
      .catch(err => console.error(err));
  }, []);

  const cancelOrder = async (orderId: number) => {
    if (!reason || reason.length < 1) return alert("Sabab kiritish majburiy");
    const res = await axios.post("http://localhost:8000/orders/cancel", {
      order_id: orderId,
      reason
    });
    alert(JSON.stringify(res.data));
  }

  return (
    <div className="p-6">
      <h2 className="text-2xl font-bold mb-4">Admin panel</h2>

      <input
        type="text"
        placeholder="Bekor qilish sababi"
        value={reason}
        onChange={(e) => setReason(e.target.value)}
        className="p-2 rounded bg-gray-800 mb-4"
      />

      {orders.map((o: any) => (
        <div key={o.id} className="border p-4 rounded bg-gray-700 mb-2">
          <p>Order №: {o.order_number}</p>
          <p>Foydalanuvchi ID: {o.user_id}</p>
          <p>Status: {o.status}</p>
          <button
            className="bg-red-600 px-3 py-1 mt-2 rounded hover:bg-red-700"
            onClick={() => cancelOrder(o.id)}
          >
            ❌ Bekor qilish
          </button>
        </div>
      ))}
    </div>
  )
}
