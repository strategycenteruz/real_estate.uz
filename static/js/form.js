const tg = window.Telegram.WebApp;
tg.expand();

document.getElementById("phoneField").value = tg.initDataUnsafe?.user?.username
  ? "@" + tg.initDataUnsafe.user.username
  : "";

const form = document.getElementById("addForm");
const imageInput = document.getElementById("imageInput");
const preview = document.getElementById("previewContainer");

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

form.addEventListener("submit", function (e) {
  e.preventDefault();
  const formData = new FormData(form);
  const user_id = tg.initDataUnsafe?.user?.id || "";
  const full_name = tg.initDataUnsafe?.user?.first_name + " " + (tg.initDataUnsafe?.user?.last_name || "");
  const username = tg.initDataUnsafe?.user?.username;

  if (user_id) {
    formData.append("description", (formData.get("description") || "") + `\n\n📱 @${username} (${full_name})\nID: ${user_id}`);
  }

  for (let i = 0; i < imageInput.files.length; i++) {
    formData.append("images", imageInput.files[i]);
  }

  fetch("/api/realestates/add/", {
    method: "POST",
    body: formData
  })
    .then(res => {
      if (res.ok) {
        document.getElementById("successMsg").style.display = "block";
        form.reset();
        preview.innerHTML = "";
      } else {
        alert("❌ E’lon yuborilmadi");
      }
    })
    .catch(err => {
      alert("Xatolik: " + err);
    });
});
