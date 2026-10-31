const DATA_URL = "../../data/processed/superstore_clean.csv";

const COLORS = {
  sales: "#29B6F6",
  profit: "#00C853",
  negative: "#FF2020",
  warning: "#FFD600",
  orders: "#2979FF",
  customers: "#8E24FF",
  furniture: "#FFD600",
  office: "#00C853",
  technology: "#29B6F6",
  grid: "#DFE8EE",
  axis: "#C5D3DD",
  text: "#60758A",
  ink: "#102F4C",
};

const categoryColors = {
  Furniture: COLORS.furniture,
  "Office Supplies": COLORS.office,
  Technology: COLORS.technology,
};

const state = {
  rows: [],
  filteredRows: [],
  filters: {
    year: "",
    region: "",
    segment: "",
    category: "",
    shipMode: "",
  },
};

const currency = new Intl.NumberFormat("fr-FR", {
  style: "currency",
  currency: "USD",
  maximumFractionDigits: 0,
});
const currencyDetailed = new Intl.NumberFormat("fr-FR", {
  style: "currency",
  currency: "USD",
  maximumFractionDigits: 2,
});
const integer = new Intl.NumberFormat("fr-FR", { maximumFractionDigits: 0 });
const percent = new Intl.NumberFormat("fr-FR", {
  style: "percent",
  maximumFractionDigits: 1,
});
const monthLabel = new Intl.DateTimeFormat("fr-FR", {
  month: "short",
  year: "2-digit",
});
const fullDate = new Intl.DateTimeFormat("fr-FR", {
  day: "numeric",
  month: "short",
  year: "numeric",
});

const $ = (selector) => document.querySelector(selector);

function parseCsv(text) {
  const rows = [];
  let row = [];
  let field = "";
  let quoted = false;

  for (let index = 0; index < text.length; index += 1) {
    const character = text[index];

    if (quoted) {
      if (character === '"' && text[index + 1] === '"') {
        field += '"';
        index += 1;
      } else if (character === '"') {
        quoted = false;
      } else {
        field += character;
      }
      continue;
    }

    if (character === '"') {
      quoted = true;
    } else if (character === ",") {
      row.push(field);
      field = "";
    } else if (character === "\n") {
      row.push(field.replace(/\r$/, ""));
      rows.push(row);
      row = [];
      field = "";
    } else {
      field += character;
    }
  }

  if (field || row.length) {
    row.push(field.replace(/\r$/, ""));
    rows.push(row);
  }

  const headers = rows.shift();
  return rows
    .filter((values) => values.length === headers.length)
    .map((values) => Object.fromEntries(headers.map((header, index) => [header, values[index]])));
}

function normalizeRow(row) {
  const orderDate = new Date(`${row["Order Date"]}T00:00:00`);
  return {
    orderId: row["Order ID"],
    orderDate,
    year: String(orderDate.getFullYear()),
    monthKey: `${orderDate.getFullYear()}-${String(orderDate.getMonth() + 1).padStart(2, "0")}`,
    shipMode: row["Ship Mode"],
    customerId: row["Customer ID"],
    customerName: row["Customer Name"],
    segment: row.Segment,
    region: row.Region,
    category: row.Category,
    subCategory: row["Sub-Category"],
    sales: Number(row.Sales),
    discount: Number(row.Discount),
    profit: Number(row.Profit),
  };
}

function uniqueSorted(field) {
  return [...new Set(state.rows.map((row) => row[field]))].sort((a, b) =>
    field === "year" ? Number(a) - Number(b) : a.localeCompare(b),
  );
}

function populateFilters() {
  const configs = [
    ["#filter-year", "year"],
    ["#filter-region", "region"],
    ["#filter-segment", "segment"],
    ["#filter-category", "category"],
    ["#filter-ship-mode", "shipMode"],
  ];

  configs.forEach(([selector, field]) => {
    const select = $(selector);
    uniqueSorted(field).forEach((value) => {
      const option = document.createElement("option");
      option.value = value;
      option.textContent = value;
      select.append(option);
    });
    select.addEventListener("change", () => {
      state.filters[field] = select.value;
      updateDashboard();
    });
  });
}

function filterRows(ignoreYear = false) {
  return state.rows.filter((row) =>
    Object.entries(state.filters).every(([field, value]) => {
      if (!value || (ignoreYear && field === "year")) return true;
      return String(row[field]) === value;
    }),
  );
}

function sum(rows, field) {
  return rows.reduce((total, row) => total + row[field], 0);
}

function distinctCount(rows, field) {
  return new Set(rows.map((row) => row[field])).size;
}

function groupBy(rows, keyField, metrics = ["sales", "profit"]) {
  const grouped = new Map();
  rows.forEach((row) => {
    const key = row[keyField];
    if (!grouped.has(key)) {
      grouped.set(key, { key, count: 0, sales: 0, profit: 0, discount: 0 });
    }
    const item = grouped.get(key);
    item.count += 1;
    metrics.forEach((metric) => {
      item[metric] += row[metric];
    });
    item.discount += row.discount;
  });
  return [...grouped.values()].map((item) => ({
    ...item,
    averageDiscount: item.count ? item.discount / item.count : 0,
  }));
}

function formatCompact(value, currencySymbol = false) {
  const absolute = Math.abs(value);
  let formatted;
  if (absolute >= 1_000_000) formatted = `${(value / 1_000_000).toFixed(1)} M`;
  else if (absolute >= 1_000) formatted = `${(value / 1_000).toFixed(0)} k`;
  else formatted = integer.format(value);
  return currencySymbol ? `${formatted} $` : formatted;
}

function formatKpiCurrency(value) {
  if (Math.abs(value) >= 1_000_000) {
    return `${(value / 1_000_000).toLocaleString("fr-FR", {
      minimumFractionDigits: 2,
      maximumFractionDigits: 2,
    })} M $`;
  }
  return currency.format(value);
}

function escapeHtml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

function tooltipHtml(title, entries) {
  return `
    <strong>${escapeHtml(title)}</strong>
    ${entries
      .map(
        ([label, value]) =>
          `<span><i>${escapeHtml(label)}</i><b>${escapeHtml(value)}</b></span>`,
      )
      .join("")}
  `;
}

function showTooltip(event, html) {
  const tooltip = $("#tooltip");
  tooltip.innerHTML = html;
  tooltip.hidden = false;
  const margin = 14;
  const rect = tooltip.getBoundingClientRect();
  let left = event.clientX + margin;
  let top = event.clientY + margin;
  if (left + rect.width > window.innerWidth - margin) left = event.clientX - rect.width - margin;
  if (top + rect.height > window.innerHeight - margin) top = event.clientY - rect.height - margin;
  tooltip.style.left = `${Math.max(margin, left)}px`;
  tooltip.style.top = `${Math.max(margin, top)}px`;
}

function hideTooltip() {
  $("#tooltip").hidden = true;
}

function svgElement(tag, attributes = {}, text = "") {
  const element = document.createElementNS("http://www.w3.org/2000/svg", tag);
  Object.entries(attributes).forEach(([name, value]) => element.setAttribute(name, value));
  if (text) element.textContent = text;
  return element;
}

function createSvg(container) {
  container.innerHTML = "";
  const width = Math.max(160, container.clientWidth);
  const height = Math.max(80, container.clientHeight);
  const svg = svgElement("svg", {
    viewBox: `0 0 ${width} ${height}`,
    preserveAspectRatio: "none",
    "aria-hidden": "true",
  });
  container.append(svg);
  return { svg, width, height };
}

function renderEmpty(container, message = "Aucune donnée pour cette sélection") {
  container.innerHTML = `<div class="empty-chart">${escapeHtml(message)}</div>`;
}

function niceMax(value) {
  if (value <= 0) return 1;
  const magnitude = 10 ** Math.floor(Math.log10(value));
  return Math.ceil(value / magnitude) * magnitude;
}

function renderLineChart(container, data, metric, color, isCurrency = true) {
  if (!data.length) return renderEmpty(container);
  const { svg, width, height } = createSvg(container);
  const margin = { top: 14, right: 10, bottom: 28, left: 46 };
  const plotWidth = width - margin.left - margin.right;
  const plotHeight = height - margin.top - margin.bottom;
  const values = data.map((item) => item[metric]);
  const minValue = Math.min(0, ...values);
  const maxValue = Math.max(1, ...values);
  const range = maxValue - minValue || 1;
  const x = (index) => margin.left + (index / Math.max(1, data.length - 1)) * plotWidth;
  const y = (value) => margin.top + ((maxValue - value) / range) * plotHeight;

  for (let index = 0; index <= 3; index += 1) {
    const value = minValue + (range * index) / 3;
    const yPosition = y(value);
    svg.append(
      svgElement("line", {
        x1: margin.left,
        y1: yPosition,
        x2: width - margin.right,
        y2: yPosition,
        class: "grid-line",
      }),
      svgElement(
        "text",
        { x: margin.left - 7, y: yPosition + 3, "text-anchor": "end" },
        formatCompact(value, isCurrency),
      ),
    );
  }

  if (minValue < 0) {
    svg.append(
      svgElement("line", {
        x1: margin.left,
        y1: y(0),
        x2: width - margin.right,
        y2: y(0),
        stroke: COLORS.axis,
        "stroke-width": 1.2,
      }),
    );
  }

  const path = data
    .map((item, index) => `${index ? "L" : "M"} ${x(index)} ${y(item[metric])}`)
    .join(" ");
  const areaPath = `${path} L ${x(data.length - 1)} ${height - margin.bottom} L ${x(0)} ${
    height - margin.bottom
  } Z`;
  svg.append(
    svgElement("path", {
      d: areaPath,
      fill: color,
      "fill-opacity": 0.1,
    }),
    svgElement("path", {
      d: path,
      fill: "none",
      stroke: color,
      "stroke-width": 2.7,
      "stroke-linejoin": "round",
      "stroke-linecap": "round",
      "vector-effect": "non-scaling-stroke",
    }),
  );

  const labelStep = Math.max(1, Math.ceil(data.length / 6));
  data.forEach((item, index) => {
    svg.append(
      svgElement("circle", {
        cx: x(index),
        cy: y(item[metric]),
        r: 2.2,
        fill: color,
        stroke: "#FFFFFF",
        "stroke-width": 1,
      }),
    );
    const point = svgElement("circle", {
      cx: x(index),
      cy: y(item[metric]),
      r: 7,
      fill: "transparent",
      class: "interactive",
    });
    point.addEventListener("mousemove", (event) =>
      showTooltip(
        event,
        tooltipHtml(monthLabel.format(item.date), [
          [metric === "sales" ? "Ventes" : "Profit", currencyDetailed.format(item[metric])],
          ["Commandes", integer.format(item.orders)],
        ]),
      ),
    );
    point.addEventListener("mouseleave", hideTooltip);
    point.addEventListener("click", () => setFilter("year", String(item.date.getFullYear())));
    svg.append(point);

    if (index % labelStep === 0 || index === data.length - 1) {
      const anchor = index === 0 ? "start" : index === data.length - 1 ? "end" : "middle";
      svg.append(
        svgElement(
          "text",
          { x: x(index), y: height - 7, "text-anchor": anchor },
          monthLabel.format(item.date),
        ),
      );
    }
  });
}

function polarToCartesian(centerX, centerY, radius, angle) {
  const radians = ((angle - 90) * Math.PI) / 180;
  return {
    x: centerX + radius * Math.cos(radians),
    y: centerY + radius * Math.sin(radians),
  };
}

function donutPath(centerX, centerY, radius, innerRadius, startAngle, endAngle) {
  const outerStart = polarToCartesian(centerX, centerY, radius, endAngle);
  const outerEnd = polarToCartesian(centerX, centerY, radius, startAngle);
  const innerStart = polarToCartesian(centerX, centerY, innerRadius, startAngle);
  const innerEnd = polarToCartesian(centerX, centerY, innerRadius, endAngle);
  const largeArc = endAngle - startAngle <= 180 ? 0 : 1;
  return [
    `M ${outerStart.x} ${outerStart.y}`,
    `A ${radius} ${radius} 0 ${largeArc} 0 ${outerEnd.x} ${outerEnd.y}`,
    `L ${innerStart.x} ${innerStart.y}`,
    `A ${innerRadius} ${innerRadius} 0 ${largeArc} 1 ${innerEnd.x} ${innerEnd.y}`,
    "Z",
  ].join(" ");
}

function renderDonut(container, data) {
  if (!data.length) return renderEmpty(container);
  const { svg, width, height } = createSvg(container);
  const total = data.reduce((result, item) => result + item.sales, 0);
  const centerX = Math.min(width * 0.34, 105);
  const centerY = height / 2 + 2;
  const radius = Math.min(54, height / 2 - 10, width * 0.23);
  const innerRadius = radius * 0.64;
  let angle = 0;

  data.forEach((item) => {
    const sweep = (item.sales / total) * 360;
    const path = svgElement("path", {
      d: donutPath(centerX, centerY, radius, innerRadius, angle, angle + sweep),
      fill: categoryColors[item.key] || COLORS.orders,
      stroke: "#FFFFFF",
      "stroke-width": 2,
      class: "interactive",
    });
    path.addEventListener("mousemove", (event) =>
      showTooltip(
        event,
        tooltipHtml(item.key, [
          ["Ventes", currencyDetailed.format(item.sales)],
          ["Part du CA", percent.format(item.sales / total)],
          ["Profit", currencyDetailed.format(item.profit)],
        ]),
      ),
    );
    path.addEventListener("mouseleave", hideTooltip);
    path.addEventListener("click", () => setFilter("category", item.key));
    svg.append(path);
    angle += sweep;
  });

  svg.append(
    svgElement(
      "text",
      {
        x: centerX,
        y: centerY - 2,
        "text-anchor": "middle",
        fill: COLORS.ink,
        "font-size": 13,
        "font-weight": 650,
      },
      "100 %",
    ),
    svgElement(
      "text",
      { x: centerX, y: centerY + 13, "text-anchor": "middle", "font-size": 8 },
      "des ventes",
    ),
  );

  const legendX = Math.max(centerX + radius + 22, width * 0.58);
  const legendStart = centerY - ((data.length - 1) * 30) / 2;
  data.forEach((item, index) => {
    const y = legendStart + index * 30;
    svg.append(
      svgElement("rect", {
        x: legendX,
        y: y - 7,
        width: 9,
        height: 9,
        rx: 1,
        fill: categoryColors[item.key] || COLORS.orders,
      }),
      svgElement("text", { x: legendX + 15, y, fill: COLORS.ink }, item.key),
      svgElement(
        "text",
        { x: width - 4, y, "text-anchor": "end", "font-weight": 650 },
        percent.format(item.sales / total),
      ),
    );
  });
}

function renderHorizontalBars(container, data, options = {}) {
  if (!data.length) return renderEmpty(container);
  const { svg, width, height } = createSvg(container);
  const labelWidth = Math.min(options.labelWidth || 104, width * 0.43);
  const margin = { top: 8, right: 34, bottom: 8, left: labelWidth };
  const plotWidth = Math.max(30, width - margin.left - margin.right);
  const rowHeight = (height - margin.top - margin.bottom) / data.length;
  const minValue = Math.min(0, ...data.map((item) => item.value));
  const maxValue = Math.max(0, ...data.map((item) => item.value));
  const range = maxValue - minValue || 1;
  const zeroX = margin.left + ((0 - minValue) / range) * plotWidth;
  const scale = (value) => margin.left + ((value - minValue) / range) * plotWidth;

  svg.append(
    svgElement("line", {
      x1: zeroX,
      y1: margin.top,
      x2: zeroX,
      y2: height - margin.bottom,
      stroke: COLORS.axis,
      "stroke-width": 1,
    }),
  );

  data.forEach((item, index) => {
    const y = margin.top + index * rowHeight + rowHeight * 0.18;
    const barHeight = Math.max(5, rowHeight * 0.58);
    const valueX = scale(item.value);
    const barX = Math.min(zeroX, valueX);
    const barWidth = Math.max(1, Math.abs(valueX - zeroX));
    const color =
      typeof options.color === "function"
        ? options.color(item)
        : options.color || (item.value < 0 ? COLORS.negative : COLORS.sales);
    const label =
      item.label.length > (options.maxLabelLength || 18)
        ? `${item.label.slice(0, (options.maxLabelLength || 18) - 1)}…`
        : item.label;

    svg.append(
      svgElement(
        "text",
        {
          x: margin.left - 7,
          y: y + barHeight * 0.72,
          "text-anchor": "end",
          fill: COLORS.ink,
        },
        label,
      ),
    );

    const bar = svgElement("rect", {
      x: barX,
      y,
      width: barWidth,
      height: barHeight,
      rx: 1.5,
      fill: color,
      class: "interactive",
    });
    bar.addEventListener("mousemove", (event) =>
      showTooltip(event, options.tooltip(item)),
    );
    bar.addEventListener("mouseleave", hideTooltip);
    if (options.onClick) bar.addEventListener("click", () => options.onClick(item));
    svg.append(bar);

    const labelX = options.valueAtRight
      ? width - 2
      : item.value >= 0
        ? Math.min(width - 2, valueX + 5)
        : Math.max(2, valueX - 5);
    svg.append(
      svgElement(
        "text",
        {
          x: labelX,
          y: y + barHeight * 0.72,
          "text-anchor": options.valueAtRight ? "end" : item.value >= 0 ? "start" : "end",
          fill: item.value < 0 ? COLORS.negative : COLORS.text,
          "font-size": 8,
          "font-weight": 650,
        },
        formatCompact(item.value, true),
      ),
    );
  });
}

function renderScatter(container, data) {
  if (!data.length) return renderEmpty(container);
  const { svg, width, height } = createSvg(container);
  const margin = { top: 12, right: 18, bottom: 27, left: 46 };
  const plotWidth = width - margin.left - margin.right;
  const plotHeight = height - margin.top - margin.bottom;
  const maxDiscount = Math.max(0.1, ...data.map((item) => item.averageDiscount)) * 1.08;
  const minProfit = Math.min(0, ...data.map((item) => item.profit));
  const maxProfit = Math.max(1, ...data.map((item) => item.profit));
  const profitRange = maxProfit - minProfit || 1;
  const maxSales = Math.max(...data.map((item) => item.sales));
  const x = (value) => margin.left + (value / maxDiscount) * plotWidth;
  const y = (value) => margin.top + ((maxProfit - value) / profitRange) * plotHeight;

  for (let index = 0; index <= 3; index += 1) {
    const discount = (maxDiscount * index) / 3;
    const xPosition = x(discount);
    svg.append(
      svgElement("line", {
        x1: xPosition,
        y1: margin.top,
        x2: xPosition,
        y2: height - margin.bottom,
        class: "grid-line",
      }),
      svgElement(
        "text",
        { x: xPosition, y: height - 8, "text-anchor": "middle" },
        percent.format(discount),
      ),
    );
  }

  if (minProfit < 0) {
    svg.append(
      svgElement("line", {
        x1: margin.left,
        y1: y(0),
        x2: width - margin.right,
        y2: y(0),
        stroke: COLORS.axis,
        "stroke-width": 1.2,
      }),
    );
  }

  [minProfit, 0, maxProfit].forEach((value) => {
    if (value < minProfit || value > maxProfit) return;
    svg.append(
      svgElement(
        "text",
        { x: margin.left - 7, y: y(value) + 3, "text-anchor": "end" },
        formatCompact(value, true),
      ),
    );
  });

  data.forEach((item) => {
    const radius = 4 + Math.sqrt(item.sales / maxSales) * 10;
    const point = svgElement("circle", {
      cx: x(item.averageDiscount),
      cy: y(item.profit),
      r: radius,
      fill: categoryColors[item.category] || COLORS.orders,
      "fill-opacity": 0.76,
      stroke: "#FFFFFF",
      "stroke-width": 1.3,
      class: "interactive",
    });
    point.addEventListener("mousemove", (event) =>
      showTooltip(
        event,
        tooltipHtml(item.key, [
          ["Catégorie", item.category],
          ["Remise moyenne", percent.format(item.averageDiscount)],
          ["Ventes", currencyDetailed.format(item.sales)],
          ["Profit", currencyDetailed.format(item.profit)],
        ]),
      ),
    );
    point.addEventListener("mouseleave", hideTooltip);
    point.addEventListener("click", () => setFilter("category", item.category));
    svg.append(point);
  });
}

function updateKpis(rows) {
  const sales = sum(rows, "sales");
  const profit = sum(rows, "profit");
  const orders = distinctCount(rows, "orderId");
  const customers = distinctCount(rows, "customerId");
  const margin = sales ? profit / sales : 0;
  if (!rows.length) {
    $("#kpi-sales").textContent = formatKpiCurrency(0);
    $("#kpi-profit").textContent = formatKpiCurrency(0);
    $("#kpi-margin").textContent = percent.format(0);
    $("#kpi-orders").textContent = "0";
    $("#kpi-customers").textContent = "0";
    $("#kpi-aov").textContent = "Panier moyen : 0 $";
    $("#kpi-repeat").textContent = "Aucune ligne active";
    $("#kpi-sales-change").textContent = "Comparaison indisponible";
    $("#kpi-profit-change").textContent = "Comparaison indisponible";
    $("#kpi-margin-status").textContent = "Aucune donnée";
    return;
  }
  const selectedYear = state.filters.year
    ? Number(state.filters.year)
    : Math.max(...rows.map((row) => Number(row.year)));
  const comparisonRows = filterRows(true);
  const currentYearRows = comparisonRows.filter((row) => Number(row.year) === selectedYear);
  const previousYearRows = comparisonRows.filter((row) => Number(row.year) === selectedYear - 1);
  const currentSales = sum(currentYearRows, "sales");
  const previousSales = sum(previousYearRows, "sales");
  const currentProfit = sum(currentYearRows, "profit");
  const previousProfit = sum(previousYearRows, "profit");
  const salesChange = previousSales ? (currentSales - previousSales) / previousSales : null;
  const profitChange = previousProfit ? (currentProfit - previousProfit) / Math.abs(previousProfit) : null;

  $("#kpi-sales").textContent = formatKpiCurrency(sales);
  $("#kpi-profit").textContent = formatKpiCurrency(profit);
  $("#kpi-margin").textContent = percent.format(margin);
  $("#kpi-orders").textContent = integer.format(orders);
  $("#kpi-customers").textContent = integer.format(customers);
  $("#kpi-aov").textContent = `Panier moyen : ${currency.format(orders ? sales / orders : 0)}`;
  $("#kpi-repeat").textContent = `${integer.format(rows.length)} lignes de vente actives`;

  const profitElement = $("#kpi-profit");
  profitElement.classList.toggle("negative", profit < 0);

  setChangeText($("#kpi-sales-change"), salesChange, `vs ${selectedYear - 1}`);
  setChangeText($("#kpi-profit-change"), profitChange, `vs ${selectedYear - 1}`);

  const marginStatus = $("#kpi-margin-status");
  marginStatus.className = margin < 0 ? "negative" : margin >= 0.1 ? "positive" : "";
  marginStatus.textContent =
    margin < 0 ? "Marge négative" : margin >= 0.1 ? "Marge supérieure à 10 %" : "Marge sous 10 %";
}

function setChangeText(element, change, context) {
  element.className = "";
  if (change === null || !Number.isFinite(change)) {
    element.textContent = "Comparaison indisponible";
    return;
  }
  element.classList.add(change >= 0 ? "positive" : "negative");
  element.textContent = `${change >= 0 ? "▲" : "▼"} ${percent.format(Math.abs(change))} ${context}`;
}

function updateContext(rows) {
  if (!rows.length) {
    $("#selection-period").textContent = "Aucune période";
    $("#selection-count").textContent = "0 ligne analysée";
    return;
  }
  const dates = rows.map((row) => row.orderDate);
  const minDate = new Date(Math.min(...dates));
  const maxDate = new Date(Math.max(...dates));
  const start = new Intl.DateTimeFormat("fr-FR", { month: "short", year: "numeric" }).format(minDate);
  const end = new Intl.DateTimeFormat("fr-FR", { month: "short", year: "numeric" }).format(maxDate);
  $("#selection-period").textContent = `${start} - ${end}`;
  $("#selection-count").textContent = `${integer.format(rows.length)} lignes analysées`;
  $("#reporting-period").textContent = `USD | ${minDate.getFullYear()}-${maxDate.getFullYear()}`;
}

function renderCharts(rows) {
  const monthly = groupBy(rows, "monthKey")
    .sort((a, b) => a.key.localeCompare(b.key))
    .map((item) => ({
      ...item,
      date: new Date(`${item.key}-01T00:00:00`),
      orders: distinctCount(
        rows.filter((row) => row.monthKey === item.key),
        "orderId",
      ),
    }));
  renderLineChart($("#sales-trend"), monthly, "sales", COLORS.sales);
  renderLineChart($("#profit-trend"), monthly, "profit", COLORS.profit);

  const categoryData = groupBy(rows, "category").sort((a, b) => b.sales - a.sales);
  renderDonut($("#category-sales"), categoryData);

  const subcategoryData = groupBy(rows, "subCategory").sort((a, b) => b.profit - a.profit);
  const visibleSubcategories =
    subcategoryData.length <= 8
      ? subcategoryData
      : [...subcategoryData.slice(0, 4), ...subcategoryData.slice(-4)];
  renderHorizontalBars(
    $("#subcategory-profit"),
    visibleSubcategories.map((item) => ({
      label: item.key,
      value: item.profit,
      source: item,
    })),
    {
      labelWidth: 92,
      maxLabelLength: 15,
      valueAtRight: true,
      color: (item) => (item.value < 0 ? COLORS.negative : COLORS.profit),
      tooltip: (item) =>
        tooltipHtml(item.label, [
          ["Profit", currencyDetailed.format(item.value)],
          ["Ventes", currencyDetailed.format(item.source.sales)],
          [
            "Marge",
            percent.format(item.source.sales ? item.source.profit / item.source.sales : 0),
          ],
        ]),
    },
  );

  const regionData = groupBy(rows, "region").sort((a, b) => b.profit - a.profit);
  renderHorizontalBars(
    $("#region-profit"),
    regionData.map((item) => ({ label: item.key, value: item.profit, source: item })),
    {
      labelWidth: 50,
      maxLabelLength: 10,
      color: (item) => (item.value < 0 ? COLORS.negative : COLORS.orders),
      tooltip: (item) =>
        tooltipHtml(item.label, [
          ["Profit", currencyDetailed.format(item.value)],
          ["Ventes", currencyDetailed.format(item.source.sales)],
        ]),
      onClick: (item) => setFilter("region", item.label),
    },
  );

  const customerData = groupBy(rows, "customerName")
    .sort((a, b) => b.sales - a.sales)
    .slice(0, 10);
  renderHorizontalBars(
    $("#top-customers"),
    customerData.map((item) => ({ label: item.key, value: item.sales, source: item })),
    {
      labelWidth: 122,
      maxLabelLength: 21,
      color: COLORS.sales,
      tooltip: (item) =>
        tooltipHtml(item.label, [
          ["Ventes", currencyDetailed.format(item.value)],
          ["Profit", currencyDetailed.format(item.source.profit)],
        ]),
    },
  );

  const scatterData = groupBy(rows, "subCategory").map((item) => {
    const representative = rows.find((row) => row.subCategory === item.key);
    return { ...item, category: representative?.category || "" };
  });
  renderScatter($("#discount-profit"), scatterData);
}

function setFilter(field, value) {
  const selectorByField = {
    year: "#filter-year",
    region: "#filter-region",
    segment: "#filter-segment",
    category: "#filter-category",
    shipMode: "#filter-ship-mode",
  };
  state.filters[field] = value;
  $(selectorByField[field]).value = value;
  updateDashboard();
}

function updateDashboard() {
  state.filteredRows = filterRows();
  updateKpis(state.filteredRows);
  updateContext(state.filteredRows);
  renderCharts(state.filteredRows);
}

function resetFilters() {
  Object.keys(state.filters).forEach((field) => {
    state.filters[field] = "";
  });
  document.querySelectorAll(".filter-list select").forEach((select) => {
    select.value = "";
  });
  updateDashboard();
}

function debounce(callback, delay = 120) {
  let timeout;
  return (...args) => {
    clearTimeout(timeout);
    timeout = setTimeout(() => callback(...args), delay);
  };
}

async function initialize() {
  try {
    const response = await fetch(DATA_URL);
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    const csv = await response.text();
    state.rows = parseCsv(csv).map(normalizeRow);
    populateFilters();
    $("#reset-filters").addEventListener("click", resetFilters);
    const maxOrderDate = new Date(Math.max(...state.rows.map((row) => row.orderDate)));
    $("#last-order").textContent = `Dernière commande : ${fullDate.format(maxOrderDate)}`;
    updateDashboard();
    $("#loading").hidden = true;
  } catch (error) {
    console.error(error);
    const loading = $("#loading");
    loading.querySelector("strong").textContent = "Chargement impossible";
    loading.querySelector("span").textContent =
      "Lancez le dashboard avec le serveur local indiqué dans le README.";
    loading.querySelector(".spinner").remove();
  }
}

window.addEventListener("resize", debounce(() => renderCharts(state.filteredRows)));
initialize();
