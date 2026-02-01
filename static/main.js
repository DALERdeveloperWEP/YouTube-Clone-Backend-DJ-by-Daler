/**
 * StreamTube Main Script
 * Handles global UI interactions like sidebar toggling.
 */

lucide.createIcons({
  attrs: {
    class: "text-gray-400",
    "stroke-width": 1.5,
  },
});

document.addEventListener("DOMContentLoaded", () => {
  setupSidebar();
  setupMobileSearch();
  setupVideoUpload();
  setupChannelCreation();
  highlightActiveNav();
});

function highlightActiveNav() {
    if (document.querySelector("nav a:first-child i")) {
        document.querySelector("nav a:first-child i").classList.remove("text-gray-400");
        document.querySelector("nav a:first-child i").classList.add("text-white");
    }
}

function setupChannelCreation() {
  const openBtn = document.getElementById("create-channel-btn");
  const openBtnMobile = document.getElementById("create-channel-btn-mobile");
  const testBtn = document.getElementById("test"); 
  const modal = document.getElementById("create-channel-modal");
  const closeBtn = document.getElementById("close-channel-modal");
  const cancelBtn = document.getElementById("cancel-channel-btn");
  
  const channelNameInput = document.getElementById("channelName");
  const channelDescInput = document.getElementById("channelDescription");
  const nameCountSpan = document.getElementById("nameCount");
  const descCountSpan = document.getElementById("descriptionCount");
  
  const avatarInput = document.getElementById("avatarInput");
  const bannerInput = document.getElementById("bannerInput");

  if (modal) {
    const openModal = (e) => {
      if (e) e.preventDefault();
      modal.classList.remove("hidden");
      modal.classList.add("flex");
    };

    const closeModal = () => {
      modal.classList.add("hidden");
      modal.classList.remove("flex");
    };

    if (openBtn) openBtn.addEventListener("click", openModal);
    if (openBtnMobile) openBtnMobile.addEventListener("click", openModal);
    if (testBtn) testBtn.addEventListener("click", openModal);

    if (closeBtn) closeBtn.addEventListener("click", closeModal);
    if (cancelBtn) cancelBtn.addEventListener("click", closeModal);

    modal.addEventListener("click", (e) => {
      if (e.target === modal) {
        closeModal();
      }
    });

    // Character counters
    if (channelNameInput && nameCountSpan) {
      channelNameInput.addEventListener("input", function () {
        nameCountSpan.textContent = this.value.length;
      });
    }

    if (channelDescInput && descCountSpan) {
      channelDescInput.addEventListener("input", function () {
        descCountSpan.textContent = this.value.length;
      });
    }

    // Avatar preview
    if (avatarInput) {
        avatarInput.addEventListener('change', (e) => {
            if (e.target.files.length > 0) {
                const file = e.target.files[0];
                if (file.type.startsWith("image/")) {
                    const reader = new FileReader();
                    reader.onload = (e) => {
                        const preview = document.getElementById('avatarPreview');
                        if (preview) preview.src = e.target.result;
                    };
                    reader.readAsDataURL(file);
                }
            }
        });
    }

    // Banner preview
    if (bannerInput) {
        bannerInput.addEventListener('change', (e) => {
             if (e.target.files.length > 0) {
                const file = e.target.files[0];
                if (file.type.startsWith("image/")) {
                    const reader = new FileReader();
                    reader.onload = (e) => {
                        const preview = document.getElementById('bannerPreview');
                        if (preview) preview.src = e.target.result;
                    };
                    reader.readAsDataURL(file);
                }
            }
        });
    }
  } else {
    console.log("Channel modal NOT found");
  }
}

function setupSidebar() {
  const menuBtn = document.getElementById("menu-btn");
  const sidebar = document.getElementById("sidebar");
  const overlay = document.getElementById("sidebar-overlay");

  if (menuBtn && sidebar && overlay) {
    menuBtn.addEventListener("click", () => {
      sidebar.classList.toggle("-translate-x-full");
      sidebar.classList.toggle("translate-x-0");

      if (window.innerWidth < 1024) {
        overlay.classList.toggle("hidden");
      }
    });

    overlay.addEventListener("click", () => {
      sidebar.classList.add("-translate-x-full");
      sidebar.classList.remove("translate-x-0");
      overlay.classList.add("hidden");
    });
  }
}

function setupMobileSearch() {
  const searchBtn = document.getElementById("mobile-search-btn");
  const backBtn = document.getElementById("search-back-btn");
  const searchBar = document.getElementById("mobile-search-bar");
  const logoArea = document.getElementById("logo-area");

  if (searchBtn && searchBar && logoArea) {
    searchBtn.addEventListener("click", () => {
      searchBar.classList.remove("hidden");
      searchBar.classList.add("flex");
      logoArea.classList.add("hidden");
    });

    if (backBtn) {
      backBtn.addEventListener("click", () => {
        searchBar.classList.add("hidden");
        searchBar.classList.remove("flex");
        logoArea.classList.remove("hidden");
      });
    }
  }
}

// Video Upload Logic
let selectedFile = null;

function setupVideoUpload() {
  const createBtn = document.getElementById("create-video-btn");
  const mobileCreateBtn = document.getElementById("mobile-create-btn");
  const modal = document.getElementById("video-upload-modal");

  function requireAuthOrRedirect() {
    if (typeof window.IS_AUTHENTICATED !== 'undefined' && !window.IS_AUTHENTICATED) {
      window.location.href = "/auth/login/";
      return false;
    }
    return true;
  }

  function requireChannelRedirect() {
    if (typeof window.IS_CHANNEL !== 'undefined' && !window.IS_CHANNEL) {
       const channelModal = document.getElementById("create-channel-modal");
       if (channelModal) {
           channelModal.classList.remove("hidden");
           channelModal.classList.add("flex");
       }
       return false;
    }
    return true;
  }

  if (modal) {
    if (createBtn) {
      createBtn.addEventListener("click", () => {
        if (!requireAuthOrRedirect()) return;
        if (!requireChannelRedirect()) return;
        modal.classList.remove("hidden");
      });
    }

    if (mobileCreateBtn) {
      mobileCreateBtn.addEventListener("click", () => {
        if (!requireAuthOrRedirect()) return;
        if (!requireChannelRedirect()) return;
        modal.classList.remove("hidden");
      });
    }

    // Close on backdrop click
    modal.addEventListener("click", (e) => {
      if (e.target === modal) {
        closeModal();
      }
    });
  }

  // Drag and drop functionality
  const dropZone = document.getElementById("dropZone");
  const fileInput = document.getElementById("fileInput");

  if (dropZone && fileInput) {
    dropZone.addEventListener("dragover", (e) => {
      e.preventDefault();
      dropZone.classList.add("border-blue-500");
    });

    dropZone.addEventListener("dragleave", () => {
      dropZone.classList.remove("border-blue-500");
    });

    dropZone.addEventListener("drop", (e) => {
      e.preventDefault();
      dropZone.classList.remove("border-blue-500");
      const files = e.dataTransfer.files;
      if (files.length > 0 && files[0].type.startsWith("video/")) {
        handleFile(files[0]);
      }
    });

    fileInput.addEventListener("change", (e) => {
      if (e.target.files.length > 0) {
        handleFile(e.target.files[0]);
      }
    });
  }

  // Character counters
  const videoTitle = document.getElementById("videoTitle");
  const videoDescription = document.getElementById("videoDescription");

  if (videoTitle) {
    videoTitle.addEventListener("input", (e) => {
      document.getElementById("titleCount").textContent = e.target.value.length;
    });
  }

  if (videoDescription) {
    videoDescription.addEventListener("input", (e) => {
      document.getElementById("descCount").textContent = e.target.value.length;
    });
  }

  // Thumbnail preview
  const thumbnailInput = document.getElementById("thumbnailInput");

  if (thumbnailInput) {
    thumbnailInput.addEventListener("change", (e) => {
      if (e.target.files.length > 0) {
        const file = e.target.files[0];
        const reader = new FileReader();
        reader.onload = (e) => {
          document.getElementById("thumbnailPreview").src = e.target.result;
          document
            .getElementById("thumbnailPreview")
            .classList.remove("hidden");
          document
            .getElementById("thumbnailPlaceholder")
            .classList.add("hidden");
        };
        reader.readAsDataURL(file);
      }
    });
  }
}

function handleFile(file) {
  selectedFile = file;
  document.getElementById("fileName").textContent = file.name;
  document.getElementById("fileSize").textContent = formatFileSize(file.size);
  document.getElementById("filePreview").classList.remove("hidden");
  document.getElementById("dropZone").classList.add("hidden");
  document.getElementById("nextBtn").disabled = false;

  // Simulate upload progress
  simulateUpload();
}

function formatFileSize(bytes) {
  if (bytes === 0) return "0 Bytes";
  const k = 1024;
  const sizes = ["Bytes", "KB", "MB", "GB"];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return Math.round((bytes / Math.pow(k, i)) * 100) / 100 + " " + sizes[i];
}

function simulateUpload() {
  const progressBar = document.getElementById("progressBar");
  const progressFill = document.getElementById("progressFill");
  const progressPercent = document.getElementById("progressPercent");

  progressBar.classList.remove("hidden");
  let progress = 0;

  const interval = setInterval(() => {
    progress += Math.random() * 15;
    if (progress >= 100) {
      progress = 100;
      clearInterval(interval);
    }
    progressFill.style.width = progress + "%";
    progressPercent.textContent = Math.round(progress) + "%";
  }, 200);
}

function removeFile() {
  selectedFile = null;
  document.getElementById("fileInput").value = "";
  document.getElementById("filePreview").classList.add("hidden");
  document.getElementById("dropZone").classList.remove("hidden");
  document.getElementById("progressBar").classList.add("hidden");
  document.getElementById("progressFill").style.width = "0%";
  document.getElementById("nextBtn").disabled = true;
}

function goToStep2() {
  document.getElementById("step1").classList.add("hidden");
  document.getElementById("step2").classList.remove("hidden");

  document
    .getElementById("step1-indicator")
    .querySelector("div")
    .classList.remove("bg-blue-500");
  document
    .getElementById("step1-indicator")
    .querySelector("div")
    .classList.add("bg-green-500");
  document
    .getElementById("step1-indicator")
    .querySelector("span")
    .classList.add("text-white/50");

  document
    .getElementById("step2-indicator")
    .querySelector("div")
    .classList.remove("bg-white/10");
  document
    .getElementById("step2-indicator")
    .querySelector("div")
    .classList.add("bg-blue-500");
  document
    .getElementById("step2-indicator")
    .querySelector("span")
    .classList.remove("text-white/50");
  document
    .getElementById("step2-indicator")
    .querySelector("span")
    .classList.add("text-white");
}

function goToStep1() {
  document.getElementById("step2").classList.add("hidden");
  document.getElementById("step1").classList.remove("hidden");

  document
    .getElementById("step1-indicator")
    .querySelector("div")
    .classList.add("bg-blue-500");
  document
    .getElementById("step1-indicator")
    .querySelector("div")
    .classList.remove("bg-green-500");
  document
    .getElementById("step1-indicator")
    .querySelector("span")
    .classList.remove("text-white/50");

  document
    .getElementById("step2-indicator")
    .querySelector("div")
    .classList.add("bg-white/10");
  document
    .getElementById("step2-indicator")
    .querySelector("div")
    .classList.remove("bg-blue-500");
  document
    .getElementById("step2-indicator")
    .querySelector("span")
    .classList.add("text-white/50");
  document
    .getElementById("step2-indicator")
    .querySelector("span")
    .classList.remove("text-white");
}

function getCSRFToken() {
  const cookie = document.cookie
    .split("; ")
    .find((row) => row.startsWith("csrftoken="));
  return cookie ? cookie.split("=")[1] : "";
}

function submitVideo() {
  console.log("submitVideo started");
  if (!selectedFile) {
    alert("Video tanlanmagan");
    return;
  }

  const title = document.getElementById("videoTitle").value;
  const description = document.getElementById("videoDescription").value;
  const categories = Array.from(
    document.getElementById("videoCategory").selectedOptions,
  ).map((o) => o.value);

  const thumbnailFile =
    document.getElementById("thumbnailInput").files[0] || null;

  if (!title || categories.length === 0) {
    alert("Title va category majburiy");
    return;
  }

  const formData = new FormData();
  formData.append("video", selectedFile);
  formData.append("title", title);
  formData.append("description", description);
  formData.append("categories", JSON.stringify(categories));
  if (thumbnailFile) formData.append("thumbnail", thumbnailFile);

  fetch("http://localhost:8000/", {
    method: "POST",
    body: formData,
  })
    .then(async (res) => {
      try {
        const data = await res.json();
        console.log("Uploaded:", data);
        alert("Video uploaded successfully!");
        closeModal();
      } catch (err) {
        console.error("Backend JSON parse xatolik:", err);
        alert("Upload tugadi, lekin backend JSON bermadi");
      }
    })
    .catch((err) => {
      console.error("Fetch xatolik:", err);
      alert("Upload xatolik bilan tugadi");
    });
}

function closeModal() {
  // Reset form
  document.getElementById("videoTitle").value = "";
  document.getElementById("videoDescription").value = "";
  removeFile();
  goToStep1();

  const modal = document.getElementById("video-upload-modal");
  if (modal) {
    modal.classList.add("hidden");
  }
}
