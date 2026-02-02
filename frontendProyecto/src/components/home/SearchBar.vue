<template>
  <div class="search-box">
    <input type="text" placeholder="Ubicación" />

    <select>
      <option disabled selected>Tipo de Propiedad</option>
      <option>Casa</option>
      <option>Departamento</option>
      <option>Terreno</option>
    </select>

    <select>
      <option disabled selected>Operación</option>
      <option>Venta</option>
      <option>Renta</option>
    </select>

    <button>Buscar Propiedades</button>
  </div>
</template>

<style scoped>
.search-box {
  background: white;
  padding: 20px;
  border-radius: 12px;
  display: grid;
  grid-template-columns: 2fr 1.5fr 1.5fr;
  gap: 15px;
  max-width: 900px;
  margin: auto;
  box-shadow: 0 15px 40px rgba(0, 0, 0, 0.25);
}

input,
select {
  padding: 12px;
  border-radius: 6px;
  border: 1px solid #d1d5db;
}

button {
  grid-column: 1 / -1;
  background: #d4af37;
  border: none;
  padding: 14px;
  font-weight: 600;
  color: #1f2937;
  border-radius: 6px;
  cursor: pointer;
}

button:hover {
  background: #c9a227;
}

/* Responsive */
@media (max-width: 900px) {
  .search-box {
    grid-template-columns: 1fr;
  }
}
</style>
