/**
 * StreamTube Main Script
 * Handles global UI interactions like sidebar toggling.
 */

document.addEventListener("DOMContentLoaded", () => {
  setupSidebar();
  setupMobileSearch();
});

function setupSidebar() {
  const menuBtn = document.getElementById("menu-btn");
  const sidebar = document.getElementById("sidebar");
  const overlay = document.getElementById("sidebar-overlay");

  if (menuBtn && sidebar && overlay) {
    menuBtn.addEventListener("click", () => {
      // Mobile: Toggle overlay and translation
      // Desktop: We might want a different behavior (collapsing),
      // but for this simple demo we'll focus on the mobile drawer pattern
      // or a simple toggle class for desktop.

      sidebar.classList.toggle("-translate-x-full");
      sidebar.classList.toggle("translate-x-0");

      // Toggle overlay only on mobile/tablet where it's usually hidden
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
