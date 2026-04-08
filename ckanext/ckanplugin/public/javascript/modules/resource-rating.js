this.ckan.module('resource-rating', function ($) {
  return {

    options: {},
    initialize: function () {
      
      console.log('resource-rating iniciado');
      console.log(this.options.resourceId);

      const self = this;

      function generateUUID() {
        if (crypto.randomUUID) {
          return crypto.randomUUID();
        } else {
          return 'anon_' + 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'
            .replace(/[xy]/g, function (c) {
              const r = Math.random() * 16 | 0;
              const v = c == 'x' ? r : (r & 0x3 | 0x8);
              return v.toString(16);
            });
        }
      }

      // ---- USER ID ----
      if (!localStorage.getItem('ratingUserId')) {
        localStorage.setItem('ratingUserId', generateUUID());
      }

      const userId = localStorage.getItem('ratingUserId');
      const resourceId = this.el.data('resource-id');
      const csrfToken = document
        .querySelector('meta[name="_csrf_token"]')
        .getAttribute('content');

      let currentUserRating = 0;

      // ---- Render estrellas ----
      function renderStars(container, score) {
        container.empty();

        for (let i = 1; i <= 5; i++) {
          const star = $('<span>')
            .addClass('star')
            .attr('data-value', i);

          if (score >= i) {
            star.addClass('fas fa-star filled');
          } else if (score >= i - 0.5) {
            star.addClass('fas fa-star-half-alt filled');
          } else {
            star.addClass('far fa-star');
          }

          container.append(star);
        }
      }

      function fetchRatings() {
        $.ajax({
          url: '/api/3/action/resource_rating_get',
          type: 'POST',
          contentType: 'application/json',
          headers: { 'X-CSRF-Token': csrfToken },
          data: JSON.stringify({
            resource_id: resourceId,
            user_id: userId
          }),
          success: function (data) {
            const result = data.result;
            console.log(data);       // 👈 agrega esto
            console.log(data.result);

            renderStars(self.$('#avg-stars'), result.average || 0);
            self.$('#avg-score').text((result.average || 0).toFixed(1));

            currentUserRating = result['user-rating'] || 0;
            console.log(currentUserRating); 
            renderStars(self.$('#user-stars'), currentUserRating);

            if (currentUserRating) {
              self.$('#user-label').text(`(${currentUserRating} estrellas)`);
            } else {
              self.$('#user-label').text('(sin calificación)');
            }
          }
        });
      }

      // ---- Eventos ----
      this.el.on('mouseover', '#user-stars .star', function () {
        const hoverValue = $(this).data('value');

        self.$('#user-stars .star').each(function () {
          const starVal = $(this).data('value');
          $(this)
            .removeClass('fas fa-star far fa-star')
            .addClass(starVal <= hoverValue ? 'fas fa-star filled' : 'far fa-star');
        });
      });

      this.el.on('mouseout', '#user-stars .star', function () {
        renderStars(self.$('#user-stars'), currentUserRating);
      });

      this.el.on('click', '#user-stars .star', function () {
        const rating = $(this).data('value');

        $.ajax({
          url: '/api/3/action/resource_rating_set',
          type: 'POST',
          contentType: 'application/json',
          headers: { 'X-CSRF-Token': csrfToken },
          data: JSON.stringify({
            resource_id: resourceId,
            rating: rating,
            user_id: userId
          }),
          success: function () {
            fetchRatings();
          }
        });
      });

      fetchRatings();
    }
  };
});


