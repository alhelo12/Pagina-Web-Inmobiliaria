<template>
  <div class="search-box">
    <label>
      <span>Ubicacion</span>
      <input type="text" placeholder="Ciudad o zona" />
    </label>

    <label>
      <span>Tipo</span>
      <select>
        <option disabled selected>Tipo de propiedad</option>
        <option>Casa</option>
        <option>Departamento</option>
        <option>Terreno</option>
      </select>
    </label>

    <label>
      <span>Operacion</span>
      <select>
        <option disabled selected>Operacion</option>
        <option>Venta</option>
        <option>Renta</option>
      </select>
    </label>

    <button>Buscar</button>
  </div>
</template>

<style scoped>
.search-box {
  width: min(920px, 100%);
  background: rgba(255, 253, 248, .96);
  padding: 18px;
  border-radius: 12px;
  display: grid;
  grid-template-columns: 1.4fr 1fr 1fr auto;
  gap: 12px;
  box-shadow: var(--shadow-strong);
  border: 1px solid rgba(255,255,255,.45);
}

label {
  display: grid;
  gap: 6px;
}

span {
  color: #07172d;
  font-size: 11px;
  font-weight: 900;
  letter-spacing: .12em;
  text-transform: uppercase;
}

input,
select {
  min-height: 46px;
  padding: 0 12px;
  border-radius: 8px;
  border: 1px solid #d9d2c5;
  background: white;
  color: #172842;
  font: inherit;
}

input:focus,
select:focus {
  outline: none;
  border-color: #d6a848;
  box-shadow: 0 0 0 3px rgba(214,168,72,.16);
}

button {
  align-self: end;
  min-height: 46px;
  padding: 0 24px;
  background: #d6a848;
  color: #07172d;
  border-radius: 8px;
  font-weight: 900;
  box-shadow: 0 12px 24px rgba(7,23,45,.18);
  transition: transform .2s ease, background .2s ease;
}

button:hover {
  background: #f2c46d;
  transform: translateY(-2px);
}

@media (max-width: 900px) {
  .search-box {
    grid-template-columns: 1fr;
  }
}
</style>
