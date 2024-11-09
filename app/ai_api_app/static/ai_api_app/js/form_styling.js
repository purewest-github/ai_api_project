document.addEventListener('DOMContentLoaded', function() {
    const helpTexts = document.querySelectorAll('.help-text');
    helpTexts.forEach(function(helpText) {
      helpText.style.color = '#6b7280';  // text-gray-500 equivalent
      helpText.style.fontSize = '0.875rem';  // text-sm equivalent
    });
  });