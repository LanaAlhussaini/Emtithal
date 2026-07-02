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
  fileName.textContent = file.name;
  fileSize.textContent = formatFileSize(file.size);
  filePreview.hidden = false;
  emptyState.hidden = true;
  uploadZone.classList.add("has-file");
  analyzeButton.disabled = false;
};

const clearSelectedFile = () => {
  selectedFile = null;
  fileInput.value = "";
  filePreview.hidden = true;
  emptyState.hidden = false;
  uploadZone.classList.remove("has-file");
  analyzeButton.disabled = true;
};

const updateProcessing = (progress, activeStep) => {
  progressBar.style.width = `${progress}%`;
  progressValue.textContent = `${progress}%`;

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

  removeFileButton.addEventListener("click", clearSelectedFile);

  uploadForm.addEventListener("submit", (event) => {
    event.preventDefault();
    if (!selectedFile) return;

    analyzeButton.disabled = true;
    processingPanel.hidden = false;
    updateProcessing(8, 0);

    const timeline = [
      { delay: 650, progress: 22, step: 1 },
      { delay: 1300, progress: 44, step: 2 },
      { delay: 2000, progress: 66, step: 3 },
      { delay: 2700, progress: 86, step: 4 },
      { delay: 3400, progress: 100, step: 5 },
    ];

    timeline.forEach((item) => {
      window.setTimeout(() => updateProcessing(item.progress, item.step), item.delay);
    });

    window.setTimeout(() => {
      window.location.href = "report.html";
    }, 3900);
  });
}

document.querySelectorAll("[data-print-report]").forEach((button) => {
  button.addEventListener("click", () => {
    window.print();
  });
});

const contractModal = document.querySelector("[data-contract-modal]");

document.querySelectorAll("[data-open-contract]").forEach((button) => {
  button.addEventListener("click", () => {
    contractModal.hidden = false;
    document.body.classList.add("has-modal");
  });
});

document.querySelectorAll("[data-close-contract]").forEach((button) => {
  button.addEventListener("click", () => {
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
