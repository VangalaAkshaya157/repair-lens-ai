document.addEventListener("DOMContentLoaded", () => {
  const sidebar = document.getElementById("sidebar");
  const menuButton = document.getElementById("menu-button");
  if (menuButton && sidebar) {
    menuButton.addEventListener("click", () => sidebar.classList.toggle("open"));
    document.querySelectorAll(".nav-link").forEach((link) => {
      link.addEventListener("click", () => sidebar.classList.remove("open"));
    });
  }

  const fileInput = document.getElementById("device-image");
  const uploadZone = document.getElementById("upload-zone");
  const preview = document.getElementById("file-preview");
  const previewImage = document.getElementById("preview-image");
  const fileName = document.getElementById("file-name");
  const fileSize = document.getElementById("file-size");
  const removeFile = document.getElementById("remove-file");
  let selectedFile = null;

  const clearFile = () => {
    if (!fileInput) return;
    fileInput.value = "";
    selectedFile = null;
    if (preview) preview.hidden = true;
    if (uploadZone) uploadZone.hidden = false;
  };

  const showFile = (file) => {
    if (!file || !file.type.startsWith("image/")) return;
    selectedFile = file;
    if (previewImage) previewImage.src = URL.createObjectURL(file);
    if (fileName) fileName.textContent = file.name;
    if (fileSize) fileSize.textContent = `${(file.size / 1024).toFixed(1)} KB`;
    if (preview) preview.hidden = false;
    if (uploadZone) uploadZone.hidden = true;
  };

  if (fileInput) {
    fileInput.addEventListener("change", () => showFile(fileInput.files[0]));
    if (removeFile) removeFile.addEventListener("click", clearFile);
    ["dragenter", "dragover"].forEach((eventName) => uploadZone?.addEventListener(eventName, (event) => {
      event.preventDefault();
      uploadZone.classList.add("dragover");
    }));
    ["dragleave", "drop"].forEach((eventName) => uploadZone?.addEventListener(eventName, (event) => {
      event.preventDefault();
      uploadZone.classList.remove("dragover");
    }));
    uploadZone?.addEventListener("drop", (event) => showFile(event.dataTransfer.files[0]));
  }

  const analyzeButton = document.getElementById("analyze-button");
  const resultsPreview = document.getElementById("results-preview");
  const diagnosisForm = document.getElementById("diagnosis-form");
  const resultContent = document.getElementById("result-content");
  const resultHeading = document.getElementById("result-heading-title");

  const listMarkup = (items) => {
    if (!Array.isArray(items) || items.length === 0) return "<p>No additional details were returned.</p>";
    return `<ul>${items.map((item) => `<li>${escapeHtml(item)}</li>`).join("")}</ul>`;
  };

  const escapeHtml = (value) => String(value ?? "").replace(/[&<>"']/g, (character) => ({
    "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#039;",
  }[character]));

  const renderDiagnosis = (data) => {
    const modeLabel = data.mode === "demo" ? "Demo Mode" : "Gemini AI";
    const diagnosis = data.diagnosis || data;
    const repair = data.repair || data;
    const evidence = data.evidence || {};
    if (resultHeading) resultHeading.textContent = `${modeLabel} assessment`;
    if (!resultContent) return;
    resultContent.innerHTML = `
      <article class="result-card"><span>🔍</span><strong>Possible Problem</strong><p>${escapeHtml(diagnosis.possible_problem)}</p></article>
      <article class="result-card"><span>👁</span><strong>Evidence Found</strong>${listMarkup([...(evidence.visible_evidence || []), ...(evidence.user_reported_symptoms || [])])}</article>
      <article class="result-card"><span>🧩</span><strong>Possible Causes</strong>${listMarkup(diagnosis.possible_causes)}</article>
      <article class="result-card"><span>🔩</span><strong>Likely Component</strong><p>${escapeHtml(diagnosis.likely_component)}</p></article>
      <article class="result-card"><span>🎯</span><strong>AI Confidence</strong><p><b>${escapeHtml(diagnosis.confidence_score)}%</b> · ${escapeHtml(diagnosis.confidence_label)}</p><div class="confidence-track"><i style="width:${Number(diagnosis.confidence_score) || 0}%"></i></div></article>
      <article class="result-card"><span>💰</span><strong>Estimated Repair Cost</strong><p class="result-emphasis">${escapeHtml(repair.estimated_cost)}</p><small>Price confidence: ${escapeHtml(repair.price_confidence)}</small></article>
      <article class="result-card"><span>🔗</span><strong>Price Sources</strong>${data.price_sources?.length ? listMarkup(data.price_sources) : "<p>Verified current repair pricing is unavailable.</p>"}</article>
      <article class="result-card"><span>⏱</span><strong>Estimated Repair Time</strong><p>${escapeHtml(repair.estimated_repair_time)}</p></article>
      <article class="result-card"><span>🔧</span><strong>Repair vs Replacement</strong><p class="recommendation-badge">${escapeHtml(repair.repair_or_replace)}</p><p>${escapeHtml(repair.reason)}</p></article>
      <article class="result-card"><span>🛠</span><strong>Safe Troubleshooting</strong>${listMarkup(data.troubleshooting_steps)}</article>
      <article class="result-card"><span>⚠️</span><strong>Safety Warning</strong><p>${escapeHtml(data.safety_warning)}</p></article>
      <article class="result-card"><span>👨‍🔧</span><strong>Professional Help</strong><p>${escapeHtml(data.professional_help)}</p></article>
      <article class="result-card"><span>📍</span><strong>Nearby Repair Shops</strong>${data.nearby_shops?.length ? listMarkup(data.nearby_shops.map((shop) => shop.name || shop.address || "Repair business")) : `<p>${escapeHtml(data.nearby_shops_message || "Nearby repair-shop information is currently unavailable.")}</p>`}</article>
    `;
    resultsPreview.hidden = false;
  };

  const showDiagnosisError = (message) => {
    if (resultHeading) resultHeading.textContent = "Analysis could not be completed";
    if (resultContent) resultContent.innerHTML = `<article class="result-card result-error"><span>⚠️</span><strong>Something went wrong</strong><p>${escapeHtml(message)}</p></article>`;
    if (resultsPreview) resultsPreview.hidden = false;
  };

  const showClientError = (message) => {
    if (resultHeading) resultHeading.textContent = "Please check your information";
    if (resultContent) resultContent.innerHTML = `<article class="result-card result-error"><span>⚠️</span><strong>More information is needed</strong><p>${escapeHtml(message)}</p></article>`;
    if (resultsPreview) resultsPreview.hidden = false;
  };

  analyzeButton?.addEventListener("click", async () => {
    if (!diagnosisForm) return;
    const category = diagnosisForm.elements.namedItem("device_category");
    const brand = diagnosisForm.elements.namedItem("brand");
    const model = diagnosisForm.elements.namedItem("model");
    const problem = diagnosisForm.elements.namedItem("problem_description") || diagnosisForm.elements.namedItem("problem");
    const normalizedProblem = (problem?.value || "").trim().toLowerCase().replace(/\s+/g, " ");
    const meaningless = new Set(["nothing", "ntg", "none", "idk", "no", "problem", "issue", "broken"]);
    if (!category?.value) return showClientError("Please select a device category.");
    if (!brand?.value.trim()) return showClientError("Please enter the device brand.");
    if (!model?.value.trim()) return showClientError("Please enter the device model.");
    if (!problem?.value.trim()) return showClientError("Please describe the problem.");
    if (meaningless.has(normalizedProblem) || normalizedProblem.length < 8) return showClientError("Please provide a more detailed description of the problem.");
    if (!selectedFile && !fileInput?.files?.[0]) return showClientError("Please upload an image of the device or damaged area.");
    analyzeButton.disabled = true;
    analyzeButton.classList.add("loading");
    analyzeButton.innerHTML = '<span class="loader"></span> Analyzing your device...';
    try {
      const formData = new FormData();
      formData.append("device_category", category?.value || "");
      formData.append("brand", brand?.value || "");
      formData.append("model", model?.value || "");
      formData.append("problem_description", problem?.value || "");
      formData.append("image", selectedFile || fileInput.files[0]);

      const response = await fetch("/api/diagnose", { method: "POST", body: formData });
      const data = await response.json();
      if (!response.ok || !data.success) throw new Error(data.error || "Unable to complete the analysis. Please try again.");
      renderDiagnosis(data);
    } catch (error) {
      console.error("Diagnosis request failed:", error);
      showDiagnosisError("Unable to complete the analysis. Please try again.");
    } finally {
      analyzeButton.disabled = false;
      analyzeButton.classList.remove("loading");
      analyzeButton.innerHTML = '<span class="button-spark">✦</span> Analyze Problem with AI <span>→</span>';
    }
  });

  const estimateButton = document.getElementById("estimate-button");
  const estimatorForm = document.getElementById("estimator-form");
  const estimateResults = document.getElementById("estimate-results");
  const estimateContent = document.getElementById("estimate-content");
  const money = (value) => `₹${Number(value || 0).toLocaleString("en-IN", { maximumFractionDigits: 0 })}`;
  estimateButton?.addEventListener("click", async (event) => {
    const button = event.currentTarget;
    const category = estimatorForm?.elements.namedItem("device_category");
    const brand = estimatorForm?.elements.namedItem("brand");
    const model = estimatorForm?.elements.namedItem("model");
    const quote = estimatorForm?.elements.namedItem("technician_quote");
    const problem = estimatorForm?.elements.namedItem("problem_description");
    if (!category?.value) return showEstimateError("Please select a device category.");
    if (!brand?.value.trim()) return showEstimateError("Please enter the brand.");
    if (!model?.value.trim()) return showEstimateError("Please enter the model.");
    if (!problem?.value.trim()) return showEstimateError("Please describe the repair problem.");
    if (!quote?.value || Number(quote.value) <= 0) return showEstimateError("Please enter a valid technician quoted price.");
    button.disabled = true;
    button.innerHTML = '<span class="loader"></span> Calculating estimate...';
    try {
      const formData = new FormData();
      formData.append("device_category", category.value);
      formData.append("brand", brand.value.trim());
      formData.append("model", model.value.trim());
      formData.append("technician_quote", quote.value);
      formData.append("problem_description", problem.value.trim());
      const response = await fetch("/api/cost-estimate", { method: "POST", body: formData });
      const data = await response.json();
      if (!response.ok || !data.success) throw new Error(data.error || "Unable to calculate the estimate right now. Please try again.");
      if (estimateContent) estimateContent.innerHTML = `
        <article class="result-card"><span>💳</span><strong>Technician Quote</strong><p class="result-emphasis">${money(data.technician_quote)}</p></article>
        <article class="result-card"><span>📊</span><strong>Estimated Repair Range</strong><p class="result-emphasis">${money(data.estimated_low)} – ${money(data.estimated_high)}</p></article>
        <article class="result-card"><span>✓</span><strong>Assessment</strong><p class="recommendation-badge">${escapeHtml(data.assessment)}</p><p>${escapeHtml(data.recommendation)}</p></article>
        <article class="result-card"><span>ℹ</span><strong>Important</strong><p>${escapeHtml(data.disclaimer)}</p></article>`;
      if (estimateResults) estimateResults.hidden = false;
    } catch (error) {
      console.error("Cost estimation request failed:", error);
      showEstimateError("Unable to calculate the estimate right now. Please try again.");
    } finally {
      button.disabled = false;
      button.innerHTML = "Estimate Cost <span>→</span>";
    }
  });

  function showEstimateError(message) {
    if (estimateContent) estimateContent.innerHTML = `<article class="result-card result-error"><span>⚠️</span><strong>Estimate unavailable</strong><p>${escapeHtml(message)}</p></article>`;
    if (estimateResults) estimateResults.hidden = false;
  }
});
