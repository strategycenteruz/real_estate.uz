const tg = window.Telegram.WebApp;
tg.expand();

const tg = window.Telegram.WebApp;
tg.expand();

const username = tg.initDataUnsafe.user?.username;
const user_id = tg.initDataUnsafe.user?.id;
const full_name = tg.initDataUnsafe.user?.first_name + ' ' + tg.initDataUnsafe.user?.last_name;

document.getElementById("phoneField").value = username ? "@" + username : "";

const form = document.getElementById("addForm");
const imageInput = document.getElementById("imageInput");
const preview = document.getElementById("previewContainer");

// 👁 Rasm ko‘rsatish
imageInput.addEventListener("change", function () {
  preview.innerHTML = "";
  [...this.files].forEach(file => {
    const reader = new FileReader();
    reader.onload = () => {
      const img = document.createElement("img");
      img.src = reader.result;
      img.style = "width:100px;margin:5px;border-radius:6px;";
      preview.appendChild(img);
    };
    reader.readAsDataURL(file);
  });
});

// 📤 Formani yuborish
form.addEventListener("submit", function (e) {
  e.preventDefault();
  const formData = new FormData(form);
  if (user_id) formData.append("description", (formData.get("description") || "") + `\n\n📱 ${username} / ${full_name} / ID: ${user_id}`);

  const files = imageInput.files;
  for (let i = 0; i < files.length; i++) {
    formData.append("images", files[i]);
  }

  fetch("https://your-backend.com/api/realestates/add/", {
    method: "POST",
    body: formData
  })
    .then(res => {
      if (res.ok) {
        document.getElementById("successMsg").style.display = "block";
        form.reset();
        preview.innerHTML = "";
      } else {
        alert("❌ Yuborishda xatolik");
      }
    })
    .catch(err => {
      console.error(err);
      alert("Xatolik: " + err);
    });
});


document.getElementById("phoneField").value = username ? "@" + username : "";


document.getElementById("phoneField").value = tg.initDataUnsafe?.user?.username
  ? "@" + tg.initDataUnsafe.user.username
  : "";

document.getElementById("addForm").addEventListener("submit", function (e) {
  e.preventDefault();

  const formData = new FormData(this);
  const jsonData = {};
  formData.forEach((value, key) => {
    if (value) jsonData[key] = value;
  });

  fetch("https://your-backend.com/api/realestates/add/", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(jsonData),
  })
    .then((res) => {
      if (res.ok) {
        document.getElementById("successMsg").style.display = "block";
        this.reset();
      } else {
        alert("❌ E’lon yuborilmadi");
      }
    })
    .catch((err) => {
      console.error(err);
      alert("Xatolik yuz berdi");
    });
});
