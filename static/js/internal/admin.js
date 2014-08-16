function TalksCtrl($scope, $http, $sce) {
    $scope.talks = [];
    $http.get('/admin/talks').success(function(data) {
        $scope.talks = data;
    });

    $scope.createTalk = function() {
        var data = {'title': $scope.newTitle,
                    'description': $scope.newDescription,
                    'slides_link': $scope.newSlidesLink,
                    'video_link': $scope.newVideoLink,
                    'description_link': $scope.newDescriptionLink,
                    'location': $scope.newLocation,
                    'date': $scope.newDate,
                    'image_link': $scope.newImageLink};
        $http.post("/admin/talks", data).success(function(data) {
            $scope.talks.unshift(data);
            $scope.newTitle = '';
            $scope.newDescription = '';
            $scope.newSlidesLink = '';
            $scope.newVideoLink = '';
            $scope.newImageLink = '';
            $scope.newDate = '';
            $scope.newDescriptionLink = '';
            $scope.newLocation = '';
            $('#create_talk').modal('hide');
        });
    };
    $scope.trustHTML = function(html) {
        return $sce.trustAsHtml(html);
    };
};

function TalkCtrl($scope, $http) {
    $scope.editing = false;
    $scope.init = function(talk) {
        $scope.uuid = talk.uuid;
        $scope.title = talk.title;
        $scope.imageLink = talk.image_link;
        $scope.slidesLink = talk.slides_link;
        $scope.videoLink = talk.video_link;
        $scope.description = talk.description;
        $scope.descriptionLink = talk.description_link;
        $scope.location = talk.location;
        $scope.date = talk.date;
        $scope.published = talk.published;
    };
    $scope.cancel = function() {
        $scope.editing = false;
    };
    $scope.editTalk = function() {
        $scope.editing = true;
    };
    $scope.unpublishTalk = function() {
        $scope.published = false;
        $scope.updateTalk();
    };
    $scope.publishTalk = function() {
        $scope.published = true;
        $scope.updateTalk();
    };
    $scope.updateTalk = function() {
        var data = {'title': $scope.title,
                    'description': $scope.description,
                    'slides_link': $scope.slidesLink,
                    'video_link': $scope.videoLink,
                    'description_link': $scope.descriptionLink,
                    'location': $scope.location,
                    'date': $scope.date,
                    'image_link': $scope.imageLink,
                    'published': $scope.published};
        $http.put("/admin/talks/" + $scope.uuid, data).success(function(data) {
            $scope.editing = false;
        });
    };
    $scope.goToBlog = function() {
        if ($scope.editing) {
          return;
        } else {
          $window.location = "/talk/" + $scope.uuid;
        }
    };
    $scope.deleteTalk = function() {
      var confirm = $window.confirm("Are you sure you want to delete this talk?");
      if (!confirm) {
        return;
      }
      $http.delete("/admin/talks/" + $scope.uuid).success(function(data) {
        for(var i=0; i < $scope.talks.length; i++) {
          if($scope.talks[i].uuid === $scope.uuid) {
            $scope.talks.splice(i, 1);
          }
        }
      });
    };
};

function BlogsCtrl($scope, $http) {
    $scope.blogs = [];
    $http.get('/admin/blog').success(function(response) {
        $scope.blogs = response;
    });

    $scope.createBlog = function() {
        var data = {'title': $scope.newTitle,
                    'body': $scope.newBody,
                    'image_link': $scope.newImageLink};
        $http.post("/admin/blog_post", data).success(function(data) {
            $scope.blogs.unshift(data);
            $scope.newTitle = '';
            $scope.newBody = '';
            $scope.newImageLink = '';
            $('#create_blog').modal('hide');
        });
    };
};

function BlogCtrl($scope, $http, $window, $sce) {
    $scope.init = function(blog) {
      $scope.uuid = blog.uuid;
      $scope.title = blog.title;
      $scope.body = blog.body;
      $scope.image_link = blog.image_link;
      $scope.published = blog.published;
    };
    $scope.editing = false;
    $scope.editPost = function() {
      $scope.editing = true;
    };
    $scope.goToBlog = function() {
        if ($scope.editing) {
          return;
        } else {
          $window.location = "/blog/" + $scope.uuid;
        }
    };
    $scope.cancel = function() {
      $scope.editing = false;
    };
    $scope.deleteBlog = function() {
      var confirm = $window.confirm("Are you sure you want to delete this blog post?");
      if (!confirm) {
        return;
      }
      $http.delete("/admin/blog_post/" + $scope.uuid).success(function(data) {
        for(var i=0; i < $scope.blogs.length; i++) {
          if($scope.blogs[i].uuid === $scope.uuid) {
            $scope.blogs.splice(i, 1);
          }
        }
      });
    };
    $scope.unpublishBlog = function() {
        $scope.published = false;
        $scope.updatePost();
    };
    $scope.publishBlog = function() {
        $scope.published = true;
        $scope.updatePost();
    };
    $scope.updatePost = function() {
      var data = {'title': $scope.title,
                  'body': $scope.body,
                  'image_link': $scope.image_link,
                  'published': $scope.published};
      $http.put("/admin/blog_post/" + $scope.uuid, data).success(function(data) {
        $scope.editing = false;
      });
    };
};

function GalleriesCtrl($scope, $http) {
    $scope.galleries = [];
    $scope.newName = '';
    $scope.newItems = [];
    $http.get('/admin/galleries').success(function(response) {
        $scope.galleries = response;
    });
    $scope.addNew = function() {
      var position = $scope.newItems.length + 1;
      var item = {'title': '', 'body': '', 'image_link': '', 'position': position};
      $scope.newItems.push(item);
    };

    $scope.createGallery = function() {
        var data = {'name': $scope.newName,
                    'items': $scope.newItems};
        $http.post("/admin/galleries", data).success(function(data) {
            $scope.galleries.unshift(data);
            $scope.newName = '';
            $scope.newItems = [];
            $('#create_gallery').modal('hide');
        });
    };
};

function GalleryCtrl($scope, $http, $window, $sce) {
    $scope.init = function(gallery) {
      $scope.uuid = gallery.uuid;
      $scope.name = gallery.name;
      $scope.items = gallery.items;
      $scope.published = gallery.published;
    };
    $scope.editing = false;
    $scope.editGallery = function() {
      $scope.editing = true;
    };
    $scope.addNewItem = function(position) {
      var item = {'title': '', 'body': '', 'image_link': '', 'position': position};
      $scope.items.splice(position - 1, 0, item);
      for (var i = position; i < $scope.items.length; i++) {
        $scope.items[i].position++;
      }
      $scope.editing = true;
    };
    $scope.removeItem = function(position) {
      $scope.items.splice(position - 1, 1);
      for (var i = position - 1; i < $scope.items.length; i++) {
        $scope.items[i].position--;
      }
      $scope.updateGallery();
    };
    $scope.goToGallery = function() {
        if ($scope.editing) {
          return;
        } else {
          $window.location = "/blog/" + $scope.uuid;
        }
    };
    $scope.cancel = function() {
      $scope.editing = false;
    };
    $scope.deleteGallery = function() {
      var confirm = $window.confirm("Are you sure you want to delete this gallery?");
      if (!confirm) {
        return;
      }
      $http.delete("/admin/gallery/" + $scope.uuid).success(function(data) {
        for(var i=0; i < $scope.galleries.length; i++) {
          if($scope.galleries[i].uuid === $scope.uuid) {
            $scope.galleries.splice(i, 1);
          }
        }
      });
    };
    $scope.unpublishGallery = function() {
        $scope.published = false;
        $scope.updateGallery();
    };
    $scope.publishGallery = function() {
        $scope.published = true;
        $scope.updateGallery();
    };
    $scope.updateGallery = function() {
      var data = {'name': $scope.name,
                  'items': $scope.items,
                  'published': $scope.published};
      $http.put("/admin/gallery/" + $scope.uuid, data).success(function(data) {
        $scope.editing = false;
      });
    };
};
