function GalleryCtrl($scope, $http, $log) {
  $scope.position = 0;
  $scope.items = [];
  $scope.init = function(gallery) {
    gallery = angular.fromJson(gallery);
    $scope.name = gallery.name;
    $scope.items = gallery.items;
    $scope.showItem();
    $scope.next_uuid = gallery.next_uuid;
    $scope.prev_uuid = gallery.prev_uuid;
    $scope.created_ago = gallery.created_ago;
  };
  $scope.displayPosition = function() {
    return $scope.position + 1;
  };
  $scope.updatePosition = function(position) {
    $scope.position = position - 1;
    $scope.showItem();
  };
  $scope.showItem = function() {
    var item = $scope.items[$scope.position];
    $scope.title = item.title;
    $scope.body = item.body;
    $('body').css('background-image', "url('" + item.image_link + "')");
  };
  $scope.nextItem = function() {
    $scope.position +=1;
    if ($scope.position === $scope.items.length) {
      $scope.position = 0;
    }
    $scope.showItem();
  };
  $scope.prevItem = function() {
    $scope.position -= 1;
    if ($scope.position < 0) {
      $scope.position = $scope.items.length - 1;
    }
    $scope.showItem();
  };
};
