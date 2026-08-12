import React from 'react';
import Link from 'next/link';

const EspacioCard = ({ espacio }) => {
  return (
    <div className="border rounded-lg p-4 hover:shadow-md transition-shadow duration-300">
      <h3 className="text-xl font-bold mb-2">{espacio.nombre}</h3>
      <p className="text-gray-600 mb-1"><strong>Ubicación:</strong> {espacio.ubicacion}</p>
      <p className="text-gray-600 mb-1"><strong>Capacidad:</strong> {espacio.capacidad} personas</p>
      <span className={`px-2 py-1 rounded-full text-sm font-medium ${
        espacio.estado === 'activo' 
          ? 'bg-green-100 text-green-800' 
          : espacio.estado === 'inactivo' 
            ? 'bg-red-100 text-red-800' 
            : 'bg-yellow-100 text-yellow-800'
      }`}>
        {espacio.estado.charAt(0).toUpperCase() + espacio.estado.slice(1)}
      </span>
      
      {/* Enlace para ver más detalles (opcional) */}
      <Link href={`/espacios/${espacio.id_espacio}`} className="mt-3 inline-block text-blue-600 hover:text-blue-800">
        Ver detalles
      </Link>
    </div>
  );
};

export default EspacioCard;