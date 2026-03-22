document.addEventListener('DOMContentLoaded', () => {
  const cards = document.querySelectorAll('.system-status-card');

  cards.forEach(card => {
    card.addEventListener('mouseover', () => {
      card.style.boxShadow = '0 4px 30px rgba(94,152,248,.6)';
      card.style.transition = 'box-shadow .3s ease-in-out';
    });

    card.addEventListener('mouseout', () => {
      card.style.boxShadow = 'none';
      card.style.transition = 'box-shadow .3s ease-in-out';
    });
  });
});