document.addEventListener("DOMContentLoaded", () => {
  const API_URL = "/api/realestates/";
  let allListings = [];

  const container = document.getElementById("listings");

  function renderListings(listings) {
    container.innerHTML = "";

    if (listings.length === 0) {
      container.innerHTML = "<p class='text-center'>🔍 Mos e’lon topilmadi</p>";
      return;
    }

    listings.forEach(item => {
      const col = document.createElement("div");
      col.className = "col-md-4";

      const card = document.createElement("div");
      card.className = "card h-100 shadow-sm";

      const imageUrl = item.images?.[0]?.image || "";

      card.innerHTML = `
        ${imageUrl ? `<img src="${imageUrl}" class="card-img-top" style="height:200px;object-fit:cover;">` : ""}
        <div class="card-body">
          <h5 class="card-title">${item.type_display} — ${item.location}</h5>
          <p class="card-text"><b>Xonalar:</b> ${item.rooms} | <b>Maydon:</b> ${item.area} m²</p>
          <p class="card-text"><b>Narx:</b> <strong>${item.price_usd} $</strong></p>
        </div>
      `;
      card.addEventListener("click", () => showModal(item));
      col.appendChild(card);
      container.appendChild(col);
    });
  }

  function filterListings() {
    const type = document.getElementById("typeFilter").value;
    const rooms = document.getElementById("roomsFilter").value;
    const search = document.getElementById("searchInput").value.toLowerCase();

    const filtered = allListings.filter(item => {
      const matchType = !type || item.type === type;
      const matchRooms = !rooms || (
        rooms === "3" ? item.rooms >= 3 : item.rooms == parseInt(rooms)
      );
      const matchSearch = !search || item.location.toLowerCase().includes(search);
      return matchType && matchRooms && matchSearch;
    });

    renderListings(filtered);
  }

  function showModal(item) {
    const modalBody = document.getElementById("modalBody");

    let gallery = item.images.map(img => `<img src="${img.image}" class="img-fluid mb-3">`).join("");

    modalBody.innerHTML = `
      ${gallery}
      <h4>${item.title || item.type_display} — ${item.location}</h4>
      <p><b>Maydon:</b> ${item.area} m² | <b>Xonalar:</b> ${item.rooms}</p>
      <p><b>Qavat:</b> ${item.floor} / ${item.total_floors}</p>
      <p><b>Holat:</b> ${item.condition_display}</p>
      <p><b>Narx:</b> <strong>${item.price_usd} $</strong></p>
      <p><b>Aloqa:</b> ${item.phone}</p>
      <p><i>${item.description}</i></p>
    `;

    const modal = new bootstrap.Modal(document.getElementById("detailModal"));
    modal.show();
  }

  // Filtrlarni ulash
  ["typeFilter", "roomsFilter", "searchInput"].forEach(id => {
    document.getElementById(id).addEventListener("input", filterListings);
  });

  // Ma’lumotlarni olish
  fetch(API_URL)
    .then(res => res.json())
    .then(data => {
      allListings = data;
      renderListings(allListings);
    })
    .catch(err => {
      container.innerHTML = `<p style="color:red;">❌ Xatolik: ${err.message}</p>`;
    });
});
