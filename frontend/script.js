const API = "http://127.0.0.1:5000/api";


async function loadDashboard() {

    try {

        const response =
            await fetch(`${API}/dashboard`);

        const data =
            await response.json();


        document.getElementById("income")
            .innerText =
            `₹${data.income.toLocaleString()}`;


        document.getElementById("expenses")
            .innerText =
            `₹${data.total_expenses.toLocaleString()}`;


        document.getElementById("savings")
            .innerText =
            `₹${data.savings.toLocaleString()}`;


        document.getElementById("emergency")
            .innerText =
            `₹${data.emergency_fund.toLocaleString()}`;


    } catch (error) {

        console.error(
            "Dashboard error:",
            error
        );

    }

}


loadDashboard();
/* ================================
   FINOVA AI - MOVING SMOKE BACKGROUND
   ================================ */

(function () {
    function initFinovaSmoke() {

        if (document.getElementById("finova-smoke-canvas")) {
            return;
        }

        const canvas = document.createElement("canvas");
        canvas.id = "finova-smoke-canvas";
        canvas.setAttribute("aria-hidden", "true");

        Object.assign(canvas.style, {
            position: "fixed",
            inset: "0",
            width: "100%",
            height: "100%",
            pointerEvents: "none",
            zIndex: "0"
        });

        document.body.prepend(canvas);

        const ctx = canvas.getContext("2d");

        if (!ctx) return;

        let width;
        let height;
        let dpr;

        const clouds = [];

        function random(min, max) {
            return Math.random() * (max - min) + min;
        }

        function createCloud() {
            return {
                x: random(-150, window.innerWidth + 150),
                y: random(-80, window.innerHeight + 80),
                radius: random(100, 240),
                speed: random(0.18, 0.48),
                drift: random(20, 70),
                phase: random(0, Math.PI * 2),
                phase2: random(0, Math.PI * 2),
                alpha: random(0.05, 0.11),
                sage: Math.random() < 0.55
            };
        }

        // Create many moving smoke clouds
        for (let i = 0; i < 30; i++) {
            clouds.push(createCloud());
        }

        function resizeCanvas() {

            dpr = Math.min(window.devicePixelRatio || 1, 2);

            width = window.innerWidth;
            height = window.innerHeight;

            canvas.width = Math.floor(width * dpr);
            canvas.height = Math.floor(height * dpr);

            ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
        }

        window.addEventListener("resize", resizeCanvas);

        resizeCanvas();

        let lastTime = performance.now();

        function drawCloud(cloud, time) {

            const x =
                cloud.x +
                Math.sin(
                    time * 0.00018 + cloud.phase
                ) * cloud.drift;

            const y =
                cloud.y +
                Math.cos(
                    time * 0.00013 + cloud.phase2
                ) *
                cloud.drift *
                0.55;

            /* Main smoke */

            const gradient =
                ctx.createRadialGradient(
                    x,
                    y,
                    0,
                    x,
                    y,
                    cloud.radius
                );

            if (cloud.sage) {

                gradient.addColorStop(
                    0,
                    `rgba(166,181,151,${cloud.alpha})`
                );

                gradient.addColorStop(
                    0.4,
                    `rgba(166,181,151,${cloud.alpha * 0.5})`
                );

            } else {

                gradient.addColorStop(
                    0,
                    `rgba(211,187,145,${cloud.alpha})`
                );

                gradient.addColorStop(
                    0.4,
                    `rgba(211,187,145,${cloud.alpha * 0.5})`
                );
            }

            gradient.addColorStop(
                1,
                "rgba(0,0,0,0)"
            );

            ctx.fillStyle = gradient;

            ctx.beginPath();

            ctx.arc(
                x,
                y,
                cloud.radius,
                0,
                Math.PI * 2
            );

            ctx.fill();


            /* Secondary smoke puff */

            const puffX =
                x +
                Math.sin(
                    time * 0.00025 + cloud.phase2
                ) *
                cloud.radius *
                0.7;

            const puffY =
                y +
                Math.cos(
                    time * 0.0002 + cloud.phase
                ) *
                cloud.radius *
                0.45;

            const puff =
                ctx.createRadialGradient(
                    puffX,
                    puffY,
                    0,
                    puffX,
                    puffY,
                    cloud.radius * 0.62
                );

            if (cloud.sage) {

                puff.addColorStop(
                    0,
                    `rgba(188,198,171,${cloud.alpha * 0.55})`
                );

            } else {

                puff.addColorStop(
                    0,
                    `rgba(225,207,174,${cloud.alpha * 0.5})`
                );
            }

            puff.addColorStop(
                1,
                "rgba(0,0,0,0)"
            );

            ctx.fillStyle = puff;

            ctx.beginPath();

            ctx.arc(
                puffX,
                puffY,
                cloud.radius * 0.62,
                0,
                Math.PI * 2
            );

            ctx.fill();
        }


        function animate(currentTime) {

            const delta =
                Math.min(
                    currentTime - lastTime,
                    40
                );

            lastTime = currentTime;

            ctx.clearRect(
                0,
                0,
                width,
                height
            );


            for (const cloud of clouds) {

                // Continuous left → right movement
                cloud.x +=
                    cloud.speed * delta;


                // Reset smoke after it leaves screen
                if (
                    cloud.x - cloud.radius >
                    width + 180
                ) {

                    cloud.x =
                        -cloud.radius -
                        random(50, 250);

                    cloud.y =
                        random(
                            -80,
                            height + 80
                        );
                }


                drawCloud(
                    cloud,
                    currentTime
                );
            }


            requestAnimationFrame(
                animate
            );
        }


        requestAnimationFrame(
            animate
        );
    }


    if (
        document.readyState ===
        "loading"
    ) {

        document.addEventListener(
            "DOMContentLoaded",
            initFinovaSmoke
        );

    } else {

        initFinovaSmoke();
    }

})();
/* =====================================================
   FINOVA DASHBOARD
   Spending Chart + Financial Health
   ===================================================== */

(function () {

    const API_URL = "http://127.0.0.1:5000/api";

    async function loadFinovaDashboard() {

        // Only run this code on a page that has dashboard elements
        const incomeElement = document.getElementById("income");
        const expenseElement = document.getElementById("expenses");
        const savingsElement = document.getElementById("savings");
        const emergencyElement = document.getElementById("emergency");
        const chartCanvas = document.getElementById("expenseChart");
        const scoreElement = document.querySelector(".score");

        if (!incomeElement || !chartCanvas) {
            return;
        }

        /* ==========================================
           LOAD FINANCIAL SUMMARY
           ========================================== */

        try {

            const response =
                await fetch(`${API_URL}/dashboard`);

            if (!response.ok) {
                throw new Error(
                    "Dashboard API error: " + response.status
                );
            }

            const data =
                await response.json();

            incomeElement.innerText =
                `₹${Number(data.income || 0).toLocaleString()}`;

            expenseElement.innerText =
                `₹${Number(data.total_expenses || 0).toLocaleString()}`;

            savingsElement.innerText =
                `₹${Number(data.savings || 0).toLocaleString()}`;

            emergencyElement.innerText =
                `₹${Number(data.emergency_fund || 0).toLocaleString()}`;


            /* ==========================================
               FINANCIAL HEALTH
               ========================================== */

            if (scoreElement) {

                const income =
                    Number(data.income || 0);

                const spending =
                    Number(data.total_expenses || 0);

                const savings =
                    Number(data.savings || 0);

                const emergency =
                    Number(data.emergency_fund || 0);

                let score = 50;

                if (income > 0) {

                    const spendingRatio =
                        spending / income;

                    if (spendingRatio <= 0.30) {
                        score += 20;
                    } else if (spendingRatio <= 0.50) {
                        score += 10;
                    } else if (spendingRatio > 0.80) {
                        score -= 15;
                    }
                }

                if (savings > 0) {
                    score += 15;
                }

                if (emergency > 0) {
                    score += 15;
                }

                score =
                    Math.max(
                        0,
                        Math.min(100, score)
                    );

                scoreElement.innerHTML =
                    `<span>${score}</span>`;

                const healthText =
                    score >= 75
                        ? "Good financial health"
                        : score >= 50
                            ? "Building financial health"
                            : "Needs financial attention";

                const healthDescription =
                    document.querySelector(
                        ".health-score p"
                    );

                if (healthDescription) {
                    healthDescription.innerText =
                        healthText;
                }
            }

        } catch (error) {

            console.error(
                "Dashboard data error:",
                error
            );

        }


        /* ==========================================
           SPENDING OVERVIEW
           ========================================== */

        try {

            const response =
                await fetch(`${API_URL}/expenses`);

            if (!response.ok) {
                throw new Error(
                    "Expenses API error: " +
                    response.status
                );
            }

            const expenses =
                await response.json();

            const totals = {};

            expenses.forEach(function (expense) {

                const category =
                    expense.category || "Other";

                totals[category] =
                    (totals[category] || 0) +
                    Number(expense.amount || 0);

            });


            const labels =
                Object.keys(totals);

            const values =
                Object.values(totals);


            if (
                typeof Chart === "undefined"
            ) {

                console.error(
                    "Chart.js is not loaded."
                );

                return;
            }


            if (window.finovaChart) {

                window.finovaChart.destroy();

            }


            /* Empty state */

            if (labels.length === 0) {

                const ctx =
                    chartCanvas.getContext("2d");

                chartCanvas.width =
                    chartCanvas.parentElement.clientWidth;

                chartCanvas.height = 240;

                ctx.clearRect(
                    0,
                    0,
                    chartCanvas.width,
                    chartCanvas.height
                );

                ctx.fillStyle =
                    "#858da0";

                ctx.font =
                    "15px Inter, Arial";

                ctx.textAlign =
                    "center";

                ctx.fillText(
                    "Add expenses to see your spending overview",
                    chartCanvas.width / 2,
                    120
                );

                return;
            }


            /* Create chart */

            window.finovaChart =
                new Chart(
                    chartCanvas,
                    {
                        type: "doughnut",

                        data: {

                            labels: labels,

                            datasets: [
                                {
                                    data: values,

                                    backgroundColor: [
                                        "#8b6cff",
                                        "#3cc9d8",
                                        "#19b878",
                                        "#f59e0b",
                                        "#ef5b6b",
                                        "#c084fc",
                                        "#6b7280",
                                        "#22c55e"
                                    ],

                                    borderWidth: 0,

                                    hoverOffset: 8
                                }
                            ]
                        },

                        options: {

                            responsive: true,

                            maintainAspectRatio: false,

                            cutout: "65%",

                            plugins: {

                                legend: {

                                    position: "bottom",

                                    labels: {

                                        color: "#c5cce0",

                                        padding: 16,

                                        usePointStyle: true,

                                        font: {
                                            size: 12
                                        }
                                    }
                                }
                            }
                        }
                    }
                );

        } catch (error) {

            console.error(
                "Spending chart error:",
                error
            );

        }

    }


    /* Start dashboard */

    if (
        document.readyState ===
        "loading"
    ) {

        document.addEventListener(
            "DOMContentLoaded",
            loadFinovaDashboard
        );

    } else {

        loadFinovaDashboard();

    }

})();
// =============================
// PROFILE MENU
// =============================

function toggleProfileMenu() {

    const menu = document.getElementById("profileMenu");

    if (menu) {
        menu.classList.toggle("show");
    }
}


function openProfile() {

    window.location.href = "profile.html";
}


function switchAccount() {

    window.location.href = "login.html";
}


async function logoutUser() {

    try {

        await fetch(
            "http://127.0.0.1:5000/api/logout",
            {
                method: "POST",
                credentials: "include"
            }
        );

        window.location.href = "login.html";

    } catch (error) {

        console.error("Logout error:", error);

        window.location.href = "login.html";
    }
}


// Close menu when clicking outside

document.addEventListener("click", function(event) {

    const profile =
        document.querySelector(".profile");

    const menu =
        document.getElementById("profileMenu");

    if (
        profile &&
        menu &&
        !profile.contains(event.target)
    ) {

        menu.classList.remove("show");

    }

});
// =============================
// DARK THEME SETTING
// =============================

function toggleDarkTheme(toggle) {

    if (toggle.checked) {

        document.body.classList.remove("light-theme");

        localStorage.setItem(
            "finovaTheme",
            "dark"
        );

    } else {

        document.body.classList.add("light-theme");

        localStorage.setItem(
            "finovaTheme",
            "light"
        );
    }
}


// Apply saved theme when page loads

document.addEventListener("DOMContentLoaded", function() {

    const savedTheme =
        localStorage.getItem("finovaTheme");

    const toggle =
        document.getElementById("darkThemeToggle");

    if (savedTheme === "light") {

        document.body.classList.add("light-theme");

        if (toggle) {
            toggle.checked = false;
        }

    } else {

        document.body.classList.remove("light-theme");

        if (toggle) {
            toggle.checked = true;
        }
    }

});