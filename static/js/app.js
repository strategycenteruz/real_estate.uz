fetch("http://127.0.0.1:8000/api/realestates/")
  .then(res => res.json())
  .then(data => {
    let html = "";
    data.forEach(item => {
      html += `<div>
                  <h3>${item.title}</h3>
                  <p>${item.description}</p>
                  <img src="${item.cover}" width="200">
               </div>`;
    });
    document.getElementById("listings").innerHTML = html;
  });
