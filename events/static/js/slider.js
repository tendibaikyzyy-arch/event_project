let slides = document.querySelectorAll(".slide");
let current = 0;

function showSlide(index) {
    slides.forEach((s, i) => {
        s.classList.remove("active");
        if (i === index) s.classList.add("active");
    });
}

setInterval(() => {
    current = (current + 1) % slides.length;
    showSlide(current);
}, 4000);