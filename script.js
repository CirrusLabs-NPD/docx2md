const css = `
  .zoomable-image {
    cursor: zoom-in;
  }

  .zoomable-image.zoomed {
    cursor: zoom-out;
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    display: flex;
    justify-content: center;
    align-items: center;
    background-color: rgba(0, 0, 0, 0.8);
    z-index: 9999;
  }

  .zoomable-image.zoomed img {
    max-width: 90%;
    max-height: 90%;
  }
`;

const styleElement = document.createElement("style");
styleElement.innerHTML = css;
document.head.appendChild(styleElement);

function loadMarkdown(file) {
  fetch(file)
    .then((response) => response.text())
    .then((markdown) => {
      const md = window.markdownit();
      const result = md.render(markdown);

      document.getElementById("content").innerHTML = result;

      // Attach click event listeners to links inside the loaded Markdown content
      const links = document.querySelectorAll("#content a");
      links.forEach((link) => {
        link.addEventListener("click", function (event) {
          event.preventDefault(); // Prevent default link behavior
          const href = link.getAttribute("href");
          if (href) {
            handleMenuItemClick(href); // Load the linked Markdown file
          }
        });
      });
    })
    .catch((error) => {
      console.error("Error loading Markdown file:", error);
    });
}

function handleMenuItemClick(file) {
  const menuItems = document.querySelectorAll(".dropdown-content a");

  // Toggle the "active" class on the clicked submenu item
  const clickedMenuItem = document.getElementById(
    `${file.replace(".md", "")}-menu`
  );
  if (clickedMenuItem) {
    clickedMenuItem.classList.toggle("active");
  }

  // Remove the "active" class from other submenu items
  menuItems.forEach((menuItem) => {
    if (menuItem !== clickedMenuItem) {
      menuItem.classList.remove("active");
    }
  });

  loadMarkdown(file); // Load and render the Markdown file
}

document.addEventListener("DOMContentLoaded", function () {
  const dropdowns = document.getElementsByClassName("dropdown");
  for (let i = 0; i < dropdowns.length; i++) {
    const dropdown = dropdowns[i];
    const dropbtn = dropdown.querySelector(".dropbtn");
    const dropdownContent = dropdown.querySelector(".dropdown-content");

    dropbtn.addEventListener("click", function () {
      dropdown.classList.toggle("active");
      if (dropdown.classList.contains("active")) {
        dropdownContent.style.display = "block";
      } else {
        dropdownContent.style.display = "none";
      }
    });
  }

  // Set the "Introduction" menu item as active by default
  const introductionMenuItem = document.getElementById("mobile-signup-menu");
  if (introductionMenuItem) {
    introductionMenuItem.classList.add("active");
  }

  // Load the "introduction.md" file by default
  loadMarkdown("mdfiles/introduction.md");
});