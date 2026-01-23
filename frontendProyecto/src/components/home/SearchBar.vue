<template>
  <div class="search-box">
    <input placeholder="Ubicación" />
    <select>
      <option>Tipo de Propiedad</option>
    </select>
    <select>
      <option>Operación</option>
    </select>
    <button>Buscar Propiedades</button>
  </div>
</template>

<style scoped>
.search-box {
  background: rgba(255, 255, 255, 0);
  padding: 20px;
  display: flex;
  gap: 20px;
  border-radius: 8px;
  margin-top: 30px;
  box-shadow: 0 10px 30px rgba(0,0,0,.2);
}

input, select {
  padding: 20px;
}
button {
  background: #f59e0b;
  border: none;
  color: white;
  padding: 10px 20px;
}
</style>
