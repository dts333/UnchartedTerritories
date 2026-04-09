(function () {
  const data = window.DOME_EXPLORER;
  if (!data || !Array.isArray(data.details) || data.details.length === 0) {
    return;
  }

  const domeFigure = document.getElementById("dome-figure");
  const highlightLayer = document.getElementById("highlight-layer");
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
  const figureWidth = Number(data.figureWidth) || 800;
  const figureHeight = Number(data.figureHeight) || 600;
  highlightLayer.setAttribute("viewBox", `0 0 ${figureWidth} ${figureHeight}`);

  const hotspotButtons = new Map();
  const topicButtons = new Map();
  const highlightGroups = new Map();
  const svgAttributeMap = new Map([
    ["cx", "cx"],
    ["cy", "cy"],
    ["d", "d"],
    ["fill", "fill"],
    ["height", "height"],
    ["h", "height"],
    ["r", "r"],
    ["rx", "rx"],
    ["ry", "ry"],
    ["stroke", "stroke"],
    ["strokeLinecap", "stroke-linecap"],
    ["strokeLinejoin", "stroke-linejoin"],
    ["strokeWidth", "stroke-width"],
    ["width", "width"],
    ["w", "width"],
    ["x", "x"],
    ["x1", "x1"],
    ["x2", "x2"],
    ["y", "y"],
    ["y1", "y1"],
    ["y2", "y2"],
  ]);
  let activeId = data.details[0].id;
  let hoveredId = null;

  function createSvgElement(tagName) {
    return document.createElementNS("http://www.w3.org/2000/svg", tagName);
  }

  function applySvgShapeAttributes(element, shape) {
    Object.entries(shape).forEach(([key, value]) => {
      const attributeName = svgAttributeMap.get(key);
      if (key !== "type" && attributeName) {
        element.setAttribute(attributeName, String(value));
      }
    });
  }

  function applyHighlightState() {
    const visibleId = hoveredId || activeId;

    highlightGroups.forEach((group, id) => {
      group.classList.toggle("is-visible", id === visibleId);
    });

    hotspotButtons.forEach((buttons, id) => {
      buttons.forEach((button) => {
        button.classList.toggle("is-preview", id === hoveredId);
        button.classList.toggle("is-active", id === activeId);
        button.setAttribute("aria-pressed", String(id === activeId));
      });
    });

    topicButtons.forEach((button, id) => {
      button.classList.toggle("is-preview", id === hoveredId);
      button.classList.toggle("is-active", id === activeId);
      button.setAttribute("aria-pressed", String(id === activeId));
    });
  }

  function setActive(detailId) {
    const detail = data.details.find((item) => item.id === detailId) || data.details[0];
    activeId = detail.id;

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
    applyHighlightState();
  }

  data.details.forEach((detail) => {
    const group = createSvgElement("g");
    group.classList.add("highlight-group");

    detail.highlight.forEach((shape) => {
      const element = createSvgElement(shape.type);
      applySvgShapeAttributes(element, shape);
      group.appendChild(element);
    });

    highlightLayer.appendChild(group);
    highlightGroups.set(detail.id, group);

    const buttons = [];
    (detail.regions || []).forEach((region, index) => {
      const hotspot = document.createElement("button");
      hotspot.type = "button";
      hotspot.className = "hotspot";
      hotspot.style.left = `${(region.x / figureWidth) * 100}%`;
      hotspot.style.top = `${(region.y / figureHeight) * 100}%`;
      hotspot.style.width = `${(region.w / figureWidth) * 100}%`;
      hotspot.style.height = `${(region.h / figureHeight) * 100}%`;
      hotspot.setAttribute("aria-label", detail.hotspot_label);
      if (index === 0) {
        const label = document.createElement("span");
        label.className = "hotspot-label";
        label.textContent = detail.label;
        hotspot.appendChild(label);
      }
      hotspot.addEventListener("mouseenter", () => {
        hoveredId = detail.id;
        applyHighlightState();
      });
      hotspot.addEventListener("mouseleave", () => {
        hoveredId = null;
        applyHighlightState();
      });
      hotspot.addEventListener("focus", () => {
        hoveredId = detail.id;
        applyHighlightState();
      });
      hotspot.addEventListener("blur", () => {
        hoveredId = null;
        applyHighlightState();
      });
      hotspot.addEventListener("click", () => setActive(detail.id));
      hotspots.appendChild(hotspot);
      buttons.push(hotspot);
    });
    hotspotButtons.set(detail.id, buttons);

    const topicButton = document.createElement("button");
    topicButton.type = "button";
    topicButton.className = "topic-button";
    topicButton.setAttribute("aria-pressed", "false");
    const topicLabel = document.createElement("span");
    topicLabel.className = "topic-label";
    topicLabel.textContent = detail.label;
    const topicCopy = document.createElement("span");
    topicCopy.className = "topic-copy";
    topicCopy.textContent = detail.summary;
    topicButton.append(topicLabel, topicCopy);
    topicButton.addEventListener("mouseenter", () => {
      hoveredId = detail.id;
      applyHighlightState();
    });
    topicButton.addEventListener("mouseleave", () => {
      hoveredId = null;
      applyHighlightState();
    });
    topicButton.addEventListener("focus", () => {
      hoveredId = detail.id;
      applyHighlightState();
    });
    topicButton.addEventListener("blur", () => {
      hoveredId = null;
      applyHighlightState();
    });
    topicButton.addEventListener("click", () => setActive(detail.id));
    topicList.appendChild(topicButton);
    topicButtons.set(detail.id, topicButton);
  });

  setActive(activeId);
})();
