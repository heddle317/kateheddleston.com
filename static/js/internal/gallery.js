function GalleryCtrl($scope, $http, $log) {
  $scope.position = 1;
  $scope.items = [];
  $scope.init = function(gallery) {
    gallery = angular.fromJson(gallery);
    $scope.name = gallery.name;
    $scope.author = gallery.author;
    $scope.items = gallery.items;
    $scope.titles = [];
    for (var i = 0; i < $scope.items.length; i++) {
      if ($scope.items[i].title) {
        $scope.titles.push($scope.items[i].title);
      }
    }
    $scope.next_uuid = gallery.next_uuid;
    $scope.prev_uuid = gallery.prev_uuid;
    $scope.created_ago = gallery.created_ago;
  };
  $scope.displayPosition = function() {
    return $scope.position + 1;
  };
  $scope.movePage = function(position) {
    $scope.position = position;
    var pos_str = 'item' + position;
    $.fn.fullpage.moveTo(pos_str);
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
};

$(document).ready(function() {
  $('#fullpage').fullpage({
    easing: '',
    autoScrolling: false,
  });
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
    var nextSection = $('#fullpage div.section[data-anchor="item' + nextPosition + '"]');
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
