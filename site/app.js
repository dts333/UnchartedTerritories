(function () {
  const data = window.DOME_EXPLORER;
  if (!data || !Array.isArray(data.details) || data.details.length === 0) {
    return;
  }

  const domeFigure = document.getElementById("dome-figure");
  const hotspots = document.getElementById("hotspots");
  const topicList = document.getElementById("topic-list");

  const detailKicker = document.getElementById("detail-kicker");
  const detailTitle = document.getElementById("detail-title");
  const detailSummary = document.getElementById("detail-summary");
  const detailImage = document.getElementById("detail-image");
  const detailCaption = document.getElementById("detail-caption");
  const detailBody = document.getElementById("detail-body");
  const detailFacts = document.getElementById("detail-facts");

  domeFigure.src = data.figureImage;
  domeFigure.alt = data.figureAlt;

  const hotspotButtons = new Map();
  const topicButtons = new Map();

  function setActive(detailId) {
    const detail = data.details.find((item) => item.id === detailId) || data.details[0];

    detailKicker.textContent = detail.kicker;
    detailTitle.textContent = detail.title;
    detailSummary.textContent = detail.summary;
    detailImage.src = detail.image;
    detailImage.alt = detail.title;
    detailCaption.textContent = detail.caption;

    detailBody.replaceChildren(
      ...detail.body.map((paragraph) => {
        const p = document.createElement("p");
        p.textContent = paragraph;
        return p;
      }),
    );

    detailFacts.replaceChildren(
      ...detail.facts.map((fact) => {
        const pill = document.createElement("div");
        pill.className = "fact-pill";
        pill.textContent = fact;
        return pill;
      }),
    );

    hotspotButtons.forEach((button, id) => {
      const isActive = id === detail.id;
      button.classList.toggle("is-active", isActive);
      button.setAttribute("aria-pressed", String(isActive));
    });

    topicButtons.forEach((button, id) => {
      const isActive = id === detail.id;
      button.classList.toggle("is-active", isActive);
      button.setAttribute("aria-pressed", String(isActive));
    });
  }

  data.details.forEach((detail) => {
    const hotspot = document.createElement("button");
    hotspot.type = "button";
    hotspot.className = "hotspot";
    hotspot.style.left = `${(detail.hotspot.x / 800) * 100}%`;
    hotspot.style.top = `${(detail.hotspot.y / 600) * 100}%`;
    hotspot.setAttribute("aria-label", detail.hotspot_label);
    hotspot.innerHTML = `<span class="hotspot-label">${detail.label}</span>`;
    hotspot.addEventListener("click", () => setActive(detail.id));
    hotspots.appendChild(hotspot);
    hotspotButtons.set(detail.id, hotspot);

    const topicButton = document.createElement("button");
    topicButton.type = "button";
    topicButton.className = "topic-button";
    topicButton.setAttribute("aria-pressed", "false");
    topicButton.innerHTML = `
      <span class="topic-label">${detail.label}</span>
      <span class="topic-copy">${detail.summary}</span>
    `;
    topicButton.addEventListener("click", () => setActive(detail.id));
    topicList.appendChild(topicButton);
    topicButtons.set(detail.id, topicButton);
  });

  setActive(data.details[0].id);
})();
