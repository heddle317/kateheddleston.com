angularApp.controller('PostController', ['$scope', '$http', '$log', function($scope, $http, $log) {
    $scope.position = 1;
    $http.get('/gallery/' + galleryUUID).success(function(response) {
        $scope.init(response);
    });
    $scope.init = function(gallery) {
        gallery = angular.fromJson(gallery);
        $scope.gallery = gallery;
        var $container = $('.gallery-content');
        imagesLoaded($($container), function() {
            var i;
            var item;
            for (i = 0; i < $scope.gallery.items.length; i++) {
                item = $scope.gallery.items[i];
                $scope.loadImage(item.image_name);
            }
        });
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
    $scope.navHeight = function() {
        return {"margin-top": '-' + $('#left-nav ul').height() / 2 + "px"};
    };
    $scope.loadImage = function(imageName) {
        var size = 'small';
        var image = $('#' + imageName);
        var url = $scope.gallery.base_url + '/' + imageName + '_' + size;
        image.attr('src', url);
        imagesLoaded($(image), function() {
            size = image.attr('size');
            if (size == 'small') {
                // we're all done :)
                return;
            }
            url = $scope.gallery.base_url + '/' + imageName + '_' + size;
            image.attr('src', url);
        });
    };
}]);
