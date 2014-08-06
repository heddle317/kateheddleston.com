function GalleryCtrl($scope, $http, $log) {
  $scope.position = 0;
  $scope.items = [];
  $scope.init = function(gallery) {
    gallery = angular.fromJson(gallery);
    $scope.name = gallery.name;
    $scope.items = gallery.items;
    $scope.showItem();
    $('body').css('background-color', "#999999");
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
