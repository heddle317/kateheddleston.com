function GalleryCtrl($scope, $http, $log) {
  $scope.position = 1;
  $scope.items = [];
  $scope.init = function(gallery) {
    gallery = angular.fromJson(gallery);
    $scope.name = gallery.name;
    $scope.items = gallery.items;
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
