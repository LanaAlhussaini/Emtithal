const header = document.querySelector("[data-header]");
const navToggle = document.querySelector("[data-nav-toggle]");
const navMenu = document.querySelector("[data-nav-menu]");

const syncHeader = () => {
  if (header) {
    header.classList.toggle("is-scrolled", window.scrollY > 8);
  }
};

syncHeader();
window.addEventListener("scroll", syncHeader, { passive: true });

if (navToggle && navMenu) {
  navToggle.addEventListener("click", () => {
    const isOpen = navMenu.classList.toggle("is-open");
    navToggle.setAttribute("aria-expanded", String(isOpen));
  });

  navMenu.querySelectorAll("a").forEach((link) => {
    link.addEventListener("click", () => {
      navMenu.classList.remove("is-open");
      navToggle.setAttribute("aria-expanded", "false");
    });
  });
}

/* =========================
   Upload Page
========================= */

const uploadZone = document.querySelector("[data-upload-zone]");
const emptyState = document.querySelector("[data-empty-state]");
const fileInput = document.querySelector("[data-file-input]");
const filePreview = document.querySelector("[data-file-preview]");
const fileName = document.querySelector("[data-file-name]");
const fileSize = document.querySelector("[data-file-size]");
const removeFileButton = document.querySelector("[data-remove-file]");
const analyzeButton = document.querySelector("[data-analyze-button]");
const uploadForm = document.querySelector("[data-upload-form]");
const processingPanel = document.querySelector("[data-processing]");
const progressBar = document.querySelector("[data-progress-bar]");
const progressValue = document.querySelector("[data-progress-value]");
const processingSteps = document.querySelectorAll("[data-step]");

let selectedFile = null;

const formatFileSize = (bytes) => {
  const megabytes = bytes / (1024 * 1024);
  return `${megabytes.toFixed(megabytes >= 10 ? 0 : 1)} MB`;
};

const setSelectedFile = (file) => {
  if (!file) return;

  selectedFile = file;

  if (fileName) fileName.textContent = file.name;
  if (fileSize) fileSize.textContent = formatFileSize(file.size);
  if (filePreview) filePreview.hidden = false;
  if (emptyState) emptyState.hidden = true;
  if (uploadZone) uploadZone.classList.add("has-file");
  if (analyzeButton) analyzeButton.disabled = false;
};

const clearSelectedFile = () => {
  selectedFile = null;

  if (fileInput) fileInput.value = "";
  if (filePreview) filePreview.hidden = true;
  if (emptyState) emptyState.hidden = false;
  if (uploadZone) uploadZone.classList.remove("has-file");
  if (analyzeButton) analyzeButton.disabled = true;
};

const updateProcessing = (progress, activeStep) => {
  if (progressBar) progressBar.style.width = `${progress}%`;
  if (progressValue) progressValue.textContent = `${progress}%`;

  processingSteps.forEach((step, index) => {
    step.classList.toggle("is-complete", index < activeStep);
    step.classList.toggle("is-active", index === activeStep);
  });
};

if (uploadZone && fileInput && uploadForm) {
  fileInput.addEventListener("change", () => {
    setSelectedFile(fileInput.files[0]);
  });

  ["dragenter", "dragover"].forEach((eventName) => {
    uploadZone.addEventListener(eventName, (event) => {
      event.preventDefault();
      uploadZone.classList.add("is-dragging");
    });
  });

  ["dragleave", "drop"].forEach((eventName) => {
    uploadZone.addEventListener(eventName, (event) => {
      event.preventDefault();
      uploadZone.classList.remove("is-dragging");
    });
  });

  uploadZone.addEventListener("drop", (event) => {
    const file = event.dataTransfer.files[0];

    if (file) {
      fileInput.files = event.dataTransfer.files;
      setSelectedFile(file);
    }
  });

  if (removeFileButton) {
    removeFileButton.addEventListener("click", clearSelectedFile);
  }

  uploadForm.addEventListener("submit", async (event) => {
    event.preventDefault();

    if (!selectedFile) {
      alert("اختاري ملف أولاً.");
      return;
    }

    analyzeButton.disabled = true;
    if (processingPanel) processingPanel.hidden = false;
    updateProcessing(10, 0);

    const formData = new FormData();
    formData.append("file", selectedFile);

    try {
      console.log("Sending file to backend:", selectedFile.name);

      updateProcessing(30, 1);

      console.log("Before fetch");

const response = await fetch("http://127.0.0.1:8000/analyze", {
  method: "POST",
  body: formData,
});

console.log("After fetch:", response.status);

      updateProcessing(70, 3);

      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`Backend error ${response.status}: ${errorText}`);
      }

      const result = await response.json();
      console.log("After JSON parse:", result);
      console.log("Backend result:", result);

      localStorage.setItem("imtithalResult", JSON.stringify(result));

      console.log("Saved result:", localStorage.getItem("imtithalResult"));

      updateProcessing(100, 4);

      setTimeout(() => {
        window.location.href = "report.html";
      }, 700);
    } 

   catch (error) {
      console.error("Upload/analyze error:", error);

  alert(
    "Error: " +
      error.message +
      "\n\nCheck backend terminal and Network tab."
  );

  analyzeButton.disabled = false;
  if (processingPanel) processingPanel.hidden = true;
}
    
  });
}

/* =========================
   Report Page
========================= */

const renderReport = () => {
  const savedResult = localStorage.getItem("imtithalResult");
  console.log("Saved result on report page:", savedResult);

  if (!savedResult) return;

  const result = JSON.parse(savedResult);

  const score = document.querySelector(".score-card--main strong");
  if (score) score.textContent = `${result.compliance_percentage}%`;

  const cards = document.querySelectorAll(".summary-grid .score-card strong");

  if (cards.length >= 4) {
    cards[1].textContent = result.summary.compliant;
    cards[2].textContent = result.summary.partial;
    cards[3].textContent = result.summary.missing;
  }

  const statusText = document.querySelector(".score-card--main p");
  if (statusText) {
    statusText.textContent =
      result.summary.missing > 0
        ? "الحالة العامة: يحتاج مراجعة"
        : "الحالة العامة: متوافق";
  }

  const findingsList = document.querySelector(".findings-list");
  if (!findingsList) return;

  findingsList.innerHTML = "";

  result.results.forEach((item) => {
    const statusClass =
      item.status === "Compliant"
        ? "status-pill--success"
        : item.status === "Partial"
        ? "status-pill--warning"
        : "status-pill--danger";

    const statusArabic =
      item.status === "Compliant"
        ? "متوافق"
        : item.status === "Partial"
        ? "يحتاج مراجعة"
        : "غير متوافق";

    const evidence = item.sama_evidence?.[0];

    findingsList.innerHTML += `
      <article class="finding-item">
        <div class="finding-item__top">
          <div>
            <span class="article-number">${item.id}</span>
            <h3>${item.name_ar}</h3>
          </div>
          <span class="status-pill ${statusClass}">${statusArabic}</span>
        </div>

        <div class="finding-item__body">
          <div>
            <h4>Evidence / Notes</h4>
            <p>${item.best_clause || "لم يتم العثور على بند واضح."}</p>
            ${
              evidence
                ? `<small>المصدر: ${evidence.metadata.source_title} - صفحة ${evidence.metadata.page_number}</small>`
                : ""
            }
          </div>

          <div>
            <h4>Recommendation</h4>
            <p>${item.recommendation || "لا يوجد إجراء مطلوب."}</p>
          </div>
        </div>
      </article>
    `;
  });
};

renderReport();

/* =========================
   Report Buttons / Modal
========================= */

document.querySelectorAll("[data-print-report]").forEach((button) => {
  button.addEventListener("click", () => {
    window.print();
  });
});

const contractModal = document.querySelector("[data-contract-modal]");

document.querySelectorAll("[data-open-contract]").forEach((button) => {
  button.addEventListener("click", () => {
    if (!contractModal) return;
    contractModal.hidden = false;
    document.body.classList.add("has-modal");
  });
});

document.querySelectorAll("[data-close-contract]").forEach((button) => {
  button.addEventListener("click", () => {
    if (!contractModal) return;
    contractModal.hidden = true;
    document.body.classList.remove("has-modal");
  });
});

contractModal?.addEventListener("click", (event) => {
  if (event.target === contractModal) {
    contractModal.hidden = true;
    document.body.classList.remove("has-modal");
  }
});