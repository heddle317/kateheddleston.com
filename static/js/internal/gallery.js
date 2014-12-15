angularApp.controller('PostController', ['$scope', '$http', '$log', function($scope, $http, $log) {
  $scope.position = 1;
  $scope.nextLink = null;
  $scope.prevLink = null;
  $http.get('/gallery/' + galleryUUID).success(function(response) {
      $scope.init(response);
  });
  $scope.init = function(gallery) {
    gallery = angular.fromJson(gallery);
    $scope.gallery = gallery;
    if ($scope.gallery.next_uuid) {
        $scope.nextLink = '/blog/' + $scope.gallery.next_uuid;
    }
    if ($scope.gallery.prev_uuid) {
        $scope.prevLink = '/blog/' + $scope.gallery.prev_uuid;
    }
    $scope.titles = [];
    for (var i = 0; i < $scope.gallery.items.length; i++) {
      if ($scope.gallery.items[i].title) {
        $scope.titles.push($scope.gallery.items[i].title);
      }
    }
  };
  $scope.displayPosition = function() {
    return $scope.position + 1;
  };
  $scope.movePage = function(position) {
    $scope.position = position;
    var sectionId = '#item' + position;
    $("html, body").animate({ scrollTop: $(sectionId).offset().top }, 1000);
  };
  $scope.nextItem = function() {
    $scope.position += 1;
    if ($scope.position === $scope.items.length) {
      $scope.position = 0;
    }
  };
  $scope.prevItem = function() {
    $scope.position -= 1;
    if ($scope.position < 0) {
      $scope.position = $scope.items.length - 1;
    }
  };
  $scope.isSelected = function(position) {
    if ($scope.position === position) {
      return true;
    }
    return false;
  };
  $scope.browserHeight = function() {
    return {"height": $(window).height() + "px"};
  };
}]);

$(document).ready(function() {
  $(window).on('scroll', function() {
    var items = $('div[data-anchor]');
    var item;
    var position;
    for (var i = 0; i < items.length; i++) {
      item = $(items[i]);
      position = item.attr('position');
      updatePosition(item, position);
    }
  });
  function updatePosition(section, position) {
    var nextPosition = parseInt(position, 10) + 1;
    var nextSection = $('#fullpage div.post-section[data-anchor="item' + nextPosition + '"]');
    var pageBottom = $(window).height() + $(window).scrollTop();
    var dot = $('.nav-item.item' + position);
    // if it's been scrolled past and we're not to the next section, return true
    if(section.offset().top < pageBottom && (nextSection.length === 0 || nextSection.offset().top > pageBottom)) {
      dot.addClass('selected');
    } else {
      dot.removeClass('selected');
    }
  };
});
