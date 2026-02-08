const container = document.getElementById("videoContainer");
const video = document.getElementById("mainVideo");
const controls = document.getElementById("controlsBar");
const centerBtn = document.getElementById("centerBtn");
const bottomPlayBtn = document.getElementById("bottomPlayBtn");
const bottomPlayIcon = document.getElementById("bottomPlayIcon");
const fsBtn = document.getElementById("fsBtn");
const fsIcon = document.getElementById("fsIcon");

const progressContainer = document.getElementById("progressContainer");
const progressBar = document.getElementById("progressBar");
const bufferBar = document.getElementById("bufferBar");
const hoverTime = document.getElementById("hoverTime");
const currTimeLabel = document.getElementById("currTime");
const totalTimeLabel = document.getElementById("totalTime");

const muteBtn = document.getElementById("muteBtn");
const volIcon = document.getElementById("volIcon");
const volContainer = document.getElementById("volContainer");
const volFill = document.getElementById("volFill");

const gestureFeedback = document.getElementById("gestureFeedback");
const gestureIcon = document.getElementById("gestureIcon");
const gestureBar = document.getElementById("gestureBar");
const brightnessOverlay = document.getElementById("brightnessOverlay");

// --- State ---
let isDragging = false;
let hideTimer = null;
let lastTap = 0;
let brightness = 1.0; // Simulated by opacity (1.0 = 0 overlay opacity)

// --- Formatting ---
const formatTime = (time) => {
  const min = Math.floor(time / 60);
  const sec = Math.floor(time % 60);
  return `${min}:${sec < 10 ? "0" + sec : sec}`;
};

// --- Core Functions ---
const togglePlay = () => {
  if (video.paused) {
    video.play();
    centerBtn.style.opacity = "0";
    centerBtn.style.transform = "scale(1.5)";
    setTimeout(() => (centerBtn.style.display = "none"), 300);
  } else {
    video.pause();
    centerBtn.style.display = "flex";
    // Small delay to allow display flex to apply before opacity transition
    requestAnimationFrame(() => {
      centerBtn.style.opacity = "1";
      centerBtn.style.transform = "scale(1)";
    });
  }
  updatePlayIcons();
  showControls();
};

const updatePlayIcons = () => {
  const icon = video.paused
    ? "solar:play-bold-duotone"
    : "solar:pause-bold-duotone";
  bottomPlayIcon.setAttribute("icon", icon);
};

const seek = (time) => {
  video.currentTime = Math.max(0, Math.min(time, video.duration));
  showControls();
};

const updateProgress = () => {
  if (!video.duration) return;
  const pct = (video.currentTime / video.duration) * 100;
  progressBar.style.width = `${pct}%`;
  currTimeLabel.innerText = formatTime(video.currentTime);

  // Buffer
  if (video.buffered.length > 0) {
    const bufPct =
      (video.buffered.end(video.buffered.length - 1) / video.duration) * 100;
    bufferBar.style.width = `${bufPct}%`;
  }
};

const setVolume = (val) => {
  const v = Math.max(0, Math.min(1, val));
  video.volume = v;
  video.muted = v === 0;
  volFill.style.width = `${v * 100}%`;

  if (v === 0) volIcon.setAttribute("icon", "solar:volume-cross-bold-duotone");
  else if (v < 0.5)
    volIcon.setAttribute("icon", "solar:volume-small-bold-duotone");
  else volIcon.setAttribute("icon", "solar:volume-loud-bold-duotone");
};

const toggleFullscreen = () => {
  if (!document.fullscreenElement) {
    container.requestFullscreen().catch((err) => {});
    fsIcon.setAttribute("icon", "solar:minimize-square-3-bold-duotone");
  } else {
    document.exitFullscreen();
    fsIcon.setAttribute("icon", "solar:full-screen-bold-duotone");
  }
};

// --- Event Listeners ---

// Play/Pause
centerBtn.onclick = (e) => {
  e.stopPropagation();
  togglePlay();
};
bottomPlayBtn.onclick = (e) => {
  e.stopPropagation();
  togglePlay();
};
video.onclick = () => togglePlay();

video.ontimeupdate = updateProgress;
video.onloadedmetadata = () => {
  totalTimeLabel.innerText = formatTime(video.duration);
  updateProgress();
};

video.onended = () => {
  centerBtn.style.display = "flex";
  requestAnimationFrame(() => {
    centerBtn.style.opacity = "1";
    centerBtn.style.transform = "scale(1)";
  });
  updatePlayIcons();
  showControls();
};

// Progress Bar Interaction
const handleProgressInput = (e) => {
  const rect = progressContainer.getBoundingClientRect();
  const x = e.clientX - rect.left;
  const pct = Math.max(0, Math.min(1, x / rect.width));
  return pct * video.duration;
};

progressContainer.addEventListener("mousedown", (e) => {
  isDragging = true;
  seek(handleProgressInput(e));
});

document.addEventListener("mousemove", (e) => {
  if (isDragging) seek(handleProgressInput(e));

  // Hover Tooltip logic for progress bar
  const rect = progressContainer.getBoundingClientRect();
  if (
    e.clientX >= rect.left &&
    e.clientX <= rect.right &&
    e.clientY >= rect.top &&
    e.clientY <= rect.bottom
  ) {
    const x = e.clientX - rect.left;
    const pct = x / rect.width;
    hoverTime.style.opacity = "1";
    hoverTime.style.left = `${x}px`;
    hoverTime.innerText = formatTime(pct * video.duration);
  } else {
    hoverTime.style.opacity = "0";
  }
});

document.addEventListener("mouseup", () => (isDragging = false));

// Volume Interaction
muteBtn.onclick = () => {
  video.muted = !video.muted;
  if (video.muted) volFill.style.width = "0%";
  else volFill.style.width = `${video.volume * 100}%`;
  updateIcons();
};

volContainer.addEventListener("click", (e) => {
  const rect = volContainer.getBoundingClientRect();
  const pct = (e.clientX - rect.left) / rect.width;
  setVolume(pct);
});

// Fullscreen
fsBtn.onclick = toggleFullscreen;

// --- Logic: Auto Hide Controls ---
const showControls = () => {
  container.classList.remove("cursor-hidden");
  controls.style.opacity = "1";
  clearTimeout(hideTimer);
  if (!video.paused) {
    hideTimer = setTimeout(() => {
      controls.style.opacity = "0";
      container.classList.add("cursor-hidden");
    }, 2500);
  }
};

container.onmousemove = showControls;
container.onmouseleave = () => {
  if (!video.paused) controls.style.opacity = "0";
};

// --- Logic: Keyboard Shortcuts ---
container.addEventListener("keydown", (e) => {
  if (
    ["Space", "ArrowUp", "ArrowDown", "ArrowLeft", "ArrowRight"].includes(
      e.code,
    )
  )
    e.preventDefault();

  switch (e.code) {
    case "Space":
    case "KeyK":
      togglePlay();
      break;
    case "KeyF":
      toggleFullscreen();
      break;
    case "KeyM":
      muteBtn.click();
      break;
    case "ArrowLeft":
      seek(video.currentTime - 5);
      showDoubleTapAnim("left");
      break;
    case "ArrowRight":
      seek(video.currentTime + 5);
      showDoubleTapAnim("right");
      break;
    case "ArrowUp":
      setVolume(video.volume + 0.1);
      showFeedback("vol", video.volume);
      break;
    case "ArrowDown":
      setVolume(video.volume - 0.1);
      showFeedback("vol", video.volume);
      break;
  }
});

// --- Logic: Mobile Gestures ---
let touchStartX = 0;
let touchStartY = 0;
let touchStartTime = 0;

container.addEventListener(
  "touchstart",
  (e) => {
    if (e.target.closest("#controlsBar")) return;
    touchStartX = e.touches[0].clientX;
    touchStartY = e.touches[0].clientY;
    touchStartTime = Date.now();
  },
  { passive: false },
);

container.addEventListener(
  "touchmove",
  (e) => {
    if (e.target.closest("#controlsBar")) return;
    e.preventDefault(); // Prevent scroll

    const dx = e.touches[0].clientX - touchStartX;
    const dy = touchStartY - e.touches[0].clientY; // Up is positive

    if (Math.abs(dy) > Math.abs(dx)) {
      // Vertical Swipe
      const rect = container.getBoundingClientRect();
      const isRight = touchStartX > rect.left + rect.width / 2;

      if (isRight) {
        // Volume
        const delta = dy / 200; // sensitivity
        const newVol = Math.max(0, Math.min(1, video.volume + delta));
        video.volume = newVol; // Update directly for smoothness
        if (Math.abs(dy) > 10) showFeedback("vol", newVol);
      } else {
        // Brightness (simulated)
        // Brightness 1.0 = opacity 0. Brightness 0.5 = opacity 0.5.
        const delta = dy / 200;
        brightness = Math.max(0.2, Math.min(1, brightness + delta));
        const opacity = 1 - brightness;
        brightnessOverlay.style.opacity = opacity;
        if (Math.abs(dy) > 10) showFeedback("sun", brightness);
      }
    }
  },
  { passive: false },
);

container.addEventListener("touchend", (e) => {
  const dt = Date.now() - touchStartTime;
  const dx = e.changedTouches[0].clientX - touchStartX;
  const dy = e.changedTouches[0].clientY - touchStartY;

  gestureFeedback.style.opacity = "0";

  // Tap Detection
  if (dt < 300 && Math.abs(dx) < 10 && Math.abs(dy) < 10) {
    const now = Date.now();
    if (now - lastTap < 300) {
      // Double Tap
      const rect = container.getBoundingClientRect();
      const x = e.changedTouches[0].clientX - rect.left;
      if (x < rect.width * 0.4) {
        seek(video.currentTime - 10);
        showDoubleTapAnim("left");
      } else if (x > rect.width * 0.6) {
        seek(video.currentTime + 10);
        showDoubleTapAnim("right");
      } else {
        togglePlay();
      }
      lastTap = 0;
    } else {
      // Single Tap Wait
      lastTap = now;
      setTimeout(() => {
        if (now === lastTap) {
          // Valid single tap, toggle controls
          if (controls.style.opacity === "1" && !video.paused) {
            controls.style.opacity = "0";
          } else {
            showControls();
          }
        }
      }, 305);
    }
  }
});

// --- Helpers ---
let feedbackTimer = null;
function showFeedback(type, val) {
  gestureFeedback.style.opacity = "1";
  gestureBar.style.width = `${val * 100}%`;
  if (type === "vol") {
    gestureIcon.setAttribute(
      "icon",
      val === 0
        ? "solar:volume-cross-bold-duotone"
        : "solar:volume-loud-bold-duotone",
    );
  } else {
    gestureIcon.setAttribute("icon", "solar:sun-bold-duotone");
  }

  // Auto hide after short delay
  clearTimeout(feedbackTimer);
  feedbackTimer = setTimeout(() => {
    gestureFeedback.style.opacity = "0";
  }, 800);
}

function showDoubleTapAnim(side) {
  const el = document.getElementById(
    side === "left" ? "seekLeft" : "seekRight",
  );
  el.style.opacity = "1";
  setTimeout(() => (el.style.opacity = "0"), 500);
}

// Init
setVolume(1);

// --- Subscription Logic ---
// --- Subscription Logic ---
const subscribeBtn = document.getElementById("subscribeBtn");
const unsubscribeBtn = document.getElementById("UnsubscribeBtn");
const subCountSpan = document.getElementById("subCount");

// Format helpers for count parsing
const parseExp = (text) => {
  const match = text.match(/(\d+(?:,\d+)*)/);
  return match ? parseInt(match[1].replace(/,/g, "")) : 0;
};

// Since the ID changes after updateUI, we need to handle subsequent clicks if the page doesn't reload.
// However, the listeners above are attached to the element reference found at load time.
// Changing the ID of the element doesn't remove the event listener from that element object in memory.
// BUT the logic attached to that listener (e.g. `updateUI(true)`) is hardcoded to one direction.
// So we need a smarter single listener or delegate.

// Better approach: Delegate or re-attach.
// Let's use a single event handler function that checks current state.

function handleSubscriptionClick(e) {
  const btn = e.target;
  // Check current action based on ID or text
  const isSubscribing =
    btn.id === "subscribeBtn" ||
    btn.textContent.trim().toLowerCase() === "subscribe";
  const currentCount = parseExp(subCountSpan.textContent);

  if (isSubscribing) {
    sendSubscriptionData("subscribe")
      .then(() => {
        // Perform Subscribe
        // Update UI to Unsubscribe state
        // (Note: updateUI logic adds 1, so we pass current count)

        btn.id = "UnsubscribeBtn";
        btn.textContent = "Unsubscribe";
        btn.classList.remove("bg-white", "text-black", "hover:bg-gray-200");
        btn.classList.add("bg-[#27272a]", "text-white", "hover:bg-[#3f3f46]");
        subCountSpan.textContent = `${currentCount + 1} subscribers`;
      })
      .catch((err) => console.error(err));
  } else {
    sendSubscriptionData("unsubscribe")
      .then(() => {
        // Perform Unsubscribe

        btn.id = "subscribeBtn";
        btn.textContent = "Subscribe";
        btn.classList.remove(
          "bg-[#27272a]",
          "text-white",
          "hover:bg-[#3f3f46]",
        );
        btn.classList.add("bg-white", "text-black", "hover:bg-gray-200");
        subCountSpan.textContent = `${Math.max(0, currentCount - 1)} subscribers`;
      })
      .catch((err) => console.error(err));
  }
}

// Re-attach safe listeners
if (subscribeBtn) subscribeBtn.removeEventListener("click", () => {}); // Clear old if any (not really possible here)
if (unsubscribeBtn) unsubscribeBtn.removeEventListener("click", () => {});

if (subscribeBtn) subscribeBtn.onclick = handleSubscriptionClick;
if (unsubscribeBtn) unsubscribeBtn.onclick = handleSubscriptionClick;

// --- Like/Dislike Logic ---
const likeBtn = document.getElementById("likeBtn");
const removeLikeBtn = document.getElementById("removeLikeBtn");
const dislikeBtn = document.getElementById("dislikeBtn");
const removeDislikeBtn = document.getElementById("removeDislikeBtn");
const likeCountSpan = document.getElementById("likeCount"); // Counts exist inside buttons, but ID might be duplicated if template logic isn't perfect. QuerySelector might be safer if ID is unique per render. Since 'likeCount' is reused in if/else blocks, only one should exist at a time.

function handleReactionClick(e) {
  const btn = e.currentTarget;
  const action = btn.id; // likeBtn, removeLikeBtn, dislikeBtn, removeDislikeBtn
  const countSpan = document.getElementById("likeCount");
  let currentCount = parseInt(countSpan.textContent.replace(/,/g, "") || "0");

  if (action === "likeBtn") {
    sendReactionData("like")
      .then(() => {
        // User wants to LIKE
        // Update to removeLikeBtn state
        btn.id = "removeLikeBtn";
        btn.classList.add("bg-white", "text-black");
        btn.classList.remove("text-white", "hover:bg-white/10");
        countSpan.textContent = currentCount + 1;

        // If dislike was active, deactivate it
        const currentDislike = document.getElementById("removeDislikeBtn");
        if (currentDislike) {
          currentDislike.id = "dislikeBtn";
          currentDislike.classList.remove("bg-white", "text-black");
          currentDislike.classList.add("text-white", "hover:bg-white/10");
        }
      })
      .catch((err) => console.error(err));
  } else if (action === "removeLikeBtn") {
    sendReactionData("removelike")
      .then(() => {
        // User wants to REMOVE LIKE
        // Update to likeBtn state
        btn.id = "likeBtn";
        btn.classList.remove("bg-white", "text-black");
        btn.classList.add("text-white", "hover:bg-white/10");
        countSpan.textContent = Math.max(0, currentCount - 1);
      })
      .catch((err) => console.error(err));
  } else if (action === "dislikeBtn") {
    sendReactionData("dislike")
      .then(() => {
        // User wants to DISLIKE
        // Update to removeDislikeBtn state
        btn.id = "removeDislikeBtn";
        btn.classList.add("bg-white", "text-black");
        btn.classList.remove("text-white", "hover:bg-white/10");

        // If like was active, deactivate it
        const currentLike = document.getElementById("removeLikeBtn");
        if (currentLike) {
          currentLike.id = "likeBtn";
          currentLike.classList.remove("bg-white", "text-black");
          currentLike.classList.add("text-white", "hover:bg-white/10");
          countSpan.textContent = Math.max(0, currentCount - 1);
        }
      })
      .catch((err) => console.error(err));
  } else if (action === "removeDislikeBtn") {
    sendReactionData("removedislike")
      .then(() => {
        // User wants to REMOVE DISLIKE
        // Update to dislikeBtn state
        btn.id = "dislikeBtn";
        btn.classList.remove("bg-white", "text-black");
        btn.classList.add("text-white", "hover:bg-white/10");
      })
      .catch((err) => console.error(err));
  }
}

// Attach listeners to whatever exists
if (likeBtn) likeBtn.onclick = handleReactionClick;
if (removeLikeBtn) removeLikeBtn.onclick = handleReactionClick;
if (dislikeBtn) dislikeBtn.onclick = handleReactionClick;
if (removeDislikeBtn) removeDislikeBtn.onclick = handleReactionClick;

// Unified send function for Subscription and Like/Dislike
// Note: subscription flow usually uses 'action' key, while like/dislike uses 'reaction' key per user instructions.
// Providing wrapper or handling both payload types.
function sendSubscriptionData(action) {
  return sendData({ action: action });
}

function sendReactionData(reaction) {
  return sendData({ reaction: reaction });
}

function sendData(data) {
  // Use getCSRFToken from main.js if available, or helper here
  let csrfToken = "";
  if (typeof getCSRFToken === "function") {
    csrfToken = getCSRFToken();
  } else {
    // Fallback if main.js isn't loaded or getCSRFToken is different
    const cookie = document.cookie
      .split("; ")
      .find((row) => row.startsWith("csrftoken="));
    csrfToken = cookie ? cookie.split("=")[1] : "";
  }

  return fetch(window.location.href, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-CSRFToken": csrfToken,
    },
    body: JSON.stringify(data),
  }).then((res) => {
    if (res.status === 401) {
      // Auth error, redirect to login
      window.location.href = "http://localhost:8000/auth/login/";
      throw new Error("Redirecting to login");
    }
    if (!res.ok) {
      console.error("Request returned status:", res.status);
      throw new Error("Request failed with status " + res.status);
    }
    return res;
  });
}
