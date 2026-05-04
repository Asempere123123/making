import { useState, useEffect } from "react";

const API_URL = `${window.location.protocol}//${window.location.hostname}:8000`;

export default function App() {
  const [activeTab, setActiveTab] = useState("dashboard");

  return (
    <div className="max-w-md mx-auto min-h-screen bg-gray-100 flex flex-col relative shadow-2xl">
      <Header />

      <main className="flex-1 overflow-y-auto pb-20">
        {activeTab === "dashboard" && <DashboardPage />}
        {activeTab === "history" && <HistoryPage />}
        {activeTab === "settings" && <Datos />}
      </main>

      <BottomNav activeTab={activeTab} setActiveTab={setActiveTab} />
    </div>
  );
}

function Header() {
  const [currentTime, setCurrentTime] = useState(new Date());

  useEffect(() => {
    const timer = setInterval(() => setCurrentTime(new Date()), 1000);
    return () => clearInterval(timer);
  }, []);

  const timeString = currentTime.toLocaleTimeString(["es"], {
    hour: "2-digit",
    minute: "2-digit",
  });
  const dateString = currentTime.toLocaleDateString(["es"], {
    weekday: "long",
    month: "long",
    day: "numeric",
  });

  return (
    <div className="bg-blue-600 text-white px-6 py-8 rounded-b-4xl shadow-md z-10">
      <h1 className="text-sm font-medium text-blue-200 uppercase tracking-wider">
        Panel de Control
      </h1>
      <div className="mt-2 flex justify-between items-end">
        <div>
          <p className="text-3xl font-bold">{timeString}</p>
          <p className="text-sm text-blue-100 mt-1">{dateString}</p>
        </div>
      </div>
    </div>
  );
}

function DashboardPage() {
  const [estadoActual, setEstadoActual] = useState(0);
  const [vehiculoActual, setVehiculoActual] = useState(null);

  const fetchData = async () => {
    try {
      const resEstado = await fetch(`${API_URL}/estado`);
      const dataEstado = await resEstado.json();
      setEstadoActual(dataEstado.estado_a);

      const resVehiculo = await fetch(`${API_URL}/vehiculo`);
      const dataVehiculo = await resVehiculo.json();
      setVehiculoActual(dataVehiculo.vehiculo_actual);
    } catch (error) {
      console.error("Error conectando a la API:", error);
    }
  };

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 2000);
    return () => clearInterval(interval);
  }, []);

  const handleManualControl = async (nuevoEstado) => {
    try {
      await fetch(`${API_URL}/estado`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ estado: nuevoEstado }),
      });
      fetchData();
    } catch (error) {
      console.error("Error enviando comando:", error);
    }
  };

  const getTextPosition = (stateCode) => {
    if (stateCode === 0) return "Izquierda";
    if (stateCode === 1) return "Adelante";
    if (stateCode === 2) return "Derecha";
    return "Desconocido";
  };

  const isVehiclePresent = vehiculoActual !== null;

  return (
    <div className="p-4 space-y-4 animate-in fade-in duration-300">
      <div className="bg-white rounded-2xl p-5 shadow-sm border border-gray-100">
        <h2 className="text-gray-500 font-semibold mb-4 text-sm uppercase tracking-wide">
          Estado en Vivo
        </h2>

        <div className="flex items-center justify-between mb-4 border-b pb-4">
          <div>
            <p className="text-xs text-gray-400">Posición Actual</p>
            <p className="text-2xl font-bold text-gray-800">
              {getTextPosition(estadoActual)}
            </p>
          </div>
        </div>

        <div className="space-y-3">
          <div className="flex justify-between items-center">
            <span className="text-gray-600">Presencia:</span>
            {isVehiclePresent ? (
              <span className="flex items-center text-green-600 font-medium">
                <span className="w-2 h-2 bg-green-500 rounded-full mr-2"></span>{" "}
                Detectado
              </span>
            ) : (
              <span className="flex items-center text-red-500 font-medium">
                <span className="w-2 h-2 bg-red-500 rounded-full mr-2"></span>{" "}
                Vacío
              </span>
            )}
          </div>

          {isVehiclePresent && (
            <div className="flex justify-between items-center bg-gray-50 p-3 rounded-lg">
              <span className="text-gray-600">Tipo Detectado:</span>
              <span className="font-semibold text-gray-800 capitalize">
                {vehiculoActual}
              </span>
            </div>
          )}
        </div>
      </div>

      <div className="bg-white rounded-2xl p-5 shadow-sm border border-gray-100">
        <h2 className="text-gray-500 font-semibold mb-4 text-sm uppercase tracking-wide">
          Control Manual
        </h2>

        <div className="flex gap-2">
          <button
            onClick={() => handleManualControl(0)}
            className={`flex-1 py-3 rounded-xl font-medium active:scale-95 transition-transform ${estadoActual === 0 ? "bg-blue-800 text-white" : "bg-blue-600 text-white"}`}
          >
            Izquierda
          </button>
          <button
            onClick={() => handleManualControl(1)}
            className={`flex-1 py-3 rounded-xl font-medium active:scale-95 transition-transform ${estadoActual === 1 ? "bg-blue-800 text-white" : "bg-blue-600 text-white"}`}
          >
            Adelante
          </button>
          <button
            onClick={() => handleManualControl(2)}
            className={`flex-1 py-3 rounded-xl font-medium active:scale-95 transition-transform ${estadoActual === 2 ? "bg-blue-800 text-white" : "bg-blue-600 text-white"}`}
          >
            Derecha
          </button>
        </div>
      </div>
    </div>
  );
}

function HistoryPage() {
  const [stats, setStats] = useState({
    total_vehiculos: 0,
    total_ligeros: 0,
    total_pesados: 0,
  });

  useEffect(() => {
    const fetchAnaliticas = async () => {
      try {
        const res = await fetch(`${API_URL}/analiticas`);
        const data = await res.json();
        setStats(data);
      } catch (error) {
        console.error("Error trayendo analíticas:", error);
      }
    };
    fetchAnaliticas();
  }, []);

  const ligerosPct =
    stats.total_vehiculos > 0
      ? Math.round((stats.total_ligeros / stats.total_vehiculos) * 100)
      : 0;
  const pesadosPct =
    stats.total_vehiculos > 0
      ? Math.round((stats.total_pesados / stats.total_vehiculos) * 100)
      : 0;

  return (
    <div className="p-4 space-y-4 animate-in fade-in duration-300">
      <div className="bg-white rounded-2xl p-5 shadow-sm border border-gray-100">
        <h2 className="text-gray-500 font-semibold mb-4 text-sm uppercase tracking-wide">
          Datos de Uso
        </h2>

        <div className="text-center mb-6">
          <p className="text-sm text-gray-500">Vehículos gestionados</p>
          <p className="text-4xl font-black text-blue-600">
            {stats.total_vehiculos}
          </p>
        </div>

        <h3 className="text-xs font-bold text-gray-400 uppercase mb-3">
          Por Tipo de Vehículo
        </h3>

        <div className="space-y-4">
          <div>
            <div className="flex justify-between text-sm mb-1">
              <span className="font-medium">Ligeros</span>
              <span className="text-gray-500">
                {stats.total_ligeros} ({ligerosPct}%)
              </span>
            </div>
            <div className="w-full bg-gray-100 rounded-full h-2">
              <div
                className="bg-blue-500 h-2 rounded-full transition-all duration-500"
                style={{ width: `${ligerosPct}%` }}
              ></div>
            </div>
          </div>

          <div>
            <div className="flex justify-between text-sm mb-1">
              <span className="font-medium">Pesados</span>
              <span className="text-gray-500">
                {stats.total_pesados} ({pesadosPct}%)
              </span>
            </div>
            <div className="w-full bg-gray-100 rounded-full h-2">
              <div
                className="bg-indigo-500 h-2 rounded-full transition-all duration-500"
                style={{ width: `${pesadosPct}%` }}
              ></div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

function Datos() {
  const [sensores, setSensores] = useState({
    dato1: 0,
    dato2: 0,
    dato3: 0,
    dato4: 0,
    dato5: 0,
    dato6: 0,
  });

  useEffect(() => {
    const fetchDatos = async () => {
      try {
        const res = await fetch(`${API_URL}/datos`);
        const data = await res.json();
        setSensores(data);
      } catch (error) {
        console.error("Error trayendo datos de sensores:", error);
      }
    };
    fetchDatos();

    const interval = setInterval(fetchDatos, 3000);
    return () => clearInterval(interval);
  }, []);

  const listaSensores = [
    { label: "Sensor 1", value: sensores.dato1 },
    { label: "Sensor 2", value: sensores.dato2 },
    { label: "Sensor 3", value: sensores.dato3 },
    { label: "Sensor 4", value: sensores.dato4 },
    { label: "Sensor 5", value: sensores.dato5 },
    { label: "Sensor 6", value: sensores.dato6 },
  ];

  return (
    <div className="p-4 space-y-4 animate-in fade-in duration-300">
      <div className="bg-white rounded-2xl p-5 shadow-sm border border-gray-100">
        <h2 className="text-gray-500 font-semibold mb-4 text-sm uppercase tracking-wide">
          Datos del Sistema
        </h2>

        <div className="space-y-4">
          {listaSensores.map((sensor, index) => (
            <div
              key={index}
              className="flex justify-between items-center py-2 border-b border-gray-50 last:border-0"
            >
              <span className="text-gray-700">{sensor.label}</span>
              <span className="text-blue-600 font-medium font-mono">
                {sensor.value.toFixed(2)}
              </span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

function BottomNav({ activeTab, setActiveTab }) {
  const navItems = [
    { id: "dashboard", icon: "🎛️", label: "Control" },
    { id: "history", icon: "📊", label: "Historial" },
    { id: "settings", icon: "🛠️", label: "Sistema" },
  ];

  return (
    <div className="absolute bottom-0 w-full bg-white border-t border-gray-200 pb-safe pt-2 px-6 pb-4">
      <div className="flex justify-between items-center">
        {navItems.map((item) => (
          <button
            key={item.id}
            onClick={() => setActiveTab(item.id)}
            className={`flex flex-col items-center p-2 transition-colors ${
              activeTab === item.id ? "text-blue-600" : "text-gray-400"
            }`}
          >
            <span className="text-2xl mb-1">{item.icon}</span>
            <span className="text-xs font-medium">{item.label}</span>
            <div
              className={`w-1 h-1 mt-1 rounded-full ${activeTab === item.id ? "bg-blue-600" : "bg-transparent"}`}
            />
          </button>
        ))}
      </div>
    </div>
  );
}
