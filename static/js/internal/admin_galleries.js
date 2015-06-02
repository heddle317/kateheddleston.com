angularApp.controller('AdminGalleriesController', ['$scope', '$http', '$log', function($scope, $http, $log) {
    $scope.loading = true;
    $scope.items = {'published': [], 'unpublished': [], 'archived': [], 'permanent': []};
    $scope.currentContainer = '.unpublished';
    $http.get('/admin/api/galleries').success(function(response) {
        $('.loading.main-loader').show();
        var i;
        var item;
        for (i = 0; i < response.length; i++) {
            item = response[i];
            if (item.published) {
                $scope.items['published'].push(item);
            } else if (item.archived) {
                $scope.items['archived'].push(item);
            } else if (item.permanent) {
                $scope.items['permanent'].push(item);
            } else {
                $scope.items['unpublished'].push(item);
            }
        };
        $scope.items['unpublished'].sort(function(a, b) {
            if (a.created_at < b.created_at) {
                    return 1;
                      }
            if (a.created_at > b.created_at) {
                return -1;
            }
            return 0;
        });
        $scope.changeTab('unpublished');
    });
    $scope.sortLists = function() {
    };
    $scope.removeItem = function(uuid) {
        for (var listName in $scope.items) {
            if ($scope.items.hasOwnProperty(listName)) {
                var list = $scope.items[listName];
                for (var i = 0; i < list.length; i++) {
                    if (list[i].uuid == uuid) {
                        list.splice(i, 1);
                    }
                }
            }
        };
    };
    $scope.changeTab = function(className) {
        $('.loading.main-loader').show();
        $($scope.currentContainer).hide();
        $scope.currentContainer = '.' + className;
        $($scope.currentContainer).hide();
        imagesLoaded($($scope.currentContainer), function() {
            $($scope.currentContainer).show();
            $('.loading.main-loader').hide();
            var msnry = new Masonry($scope.currentContainer, {columnWidth: 125,
                                                              itemSelector: ".item",
                                                              gutter: 10,
                                                              isFitWidth: true,
                                                              transitionDuration: 0});
        });
    };
}]);

angularApp.controller('MiniEditGalleryController', ['$scope', '$http', '$window', '$sce', '$log', function($scope, $http, $window, $sce, $log) {
    $scope.initGallery = function(gallery) {
        $scope.gallery = gallery;
        $scope.gallery_uuid = gallery.uuid;
    };
    $scope.publishGallery = function(publish) {
        var confirm = $window.confirm("Are you sure you want to publish or unpublish this blog post?");
        if (!confirm) {
            return;
        }
        $scope.gallery.published = publish;
        $scope.gallery.archived = false;
        $scope.updateGallery();
    };
    $scope.archiveGallery = function(archive) {
        $scope.gallery.archived = archive;
        $scope.updateGallery();
    };
    $scope.updateGallery = function() {
        $scope.removeItem($scope.gallery.uuid);
        if ($scope.gallery.published) {
            $scope.items.published.push($scope.gallery);
        } else if ($scope.gallery.archived) {
            $scope.items.archived.push($scope.gallery);
        } else {
            $scope.items.unpublished.push($scope.gallery);
        }
        $scope.sortLists();
        var data = {'published': $scope.gallery.published,
                    'archived': $scope.gallery.archived};
        $http.put("/admin/api/gallery/" + $scope.gallery.uuid, data).success(function(data) {
        });
    };
}]);

angularApp.controller('EditGalleryController', ['$scope', '$http', '$window', '$sce', '$log', function($scope, $http, $window, $sce, $log) {
    $scope.items = [];
    $scope.published = false;
    $scope.editing = false;
    $scope.initGallery = function(gallery) {
        $scope.gallery = gallery;
        $scope.uuid = gallery.uuid;
        $scope.gallery_uuid = gallery.uuid;
        if (!$scope.gallery_uuid) {
            $scope.editing = true;
        }
        $scope.name = gallery.name;
        $scope.subtitle = gallery.subtitle;
        $scope.author = gallery.author;
        $scope.coverPhoto = gallery.cover_photo;
        $scope.items = gallery.items;
        $scope.published = gallery.published;
        $scope.published_ago = gallery.published_ago;
    };
    if (galleryUUID) {
        $http.get('/admin/api/gallery/' + galleryUUID).success(function(response) {
            $scope.initGallery(response);
        });
    } else {
        $http.get('/admin/api/gallery').success(function(response) {
            $scope.initGallery(response);
        });
    }
    $scope.wordCount = function() {
        var count = 0;
        for (var i = 0; i < $scope.items.length; i++) {
            if ($scope.items[i].body && !$scope.items[i].dead) {
                count += $scope.items[i].body.split(" ").length;
            }
        }
        return count;
    };
    $scope.itemsArrayLength = function() {
        var arr = [];
        var i;
        for (i = 0; i < $scope.items.length; i++) {
            arr.push(i + 1);
        }
        return arr;
    };
    $scope.editGallery = function() {
      $scope.editing = true;
    };
    $scope.addNewItem = function(position) {
        var item = {'title': '',
                    'body': '',
                    'image_name': '',
                    'position': position,
                    'gallery_uuid': $scope.gallery_uuid,
                    'dead': false,
                    'comments': [],
                    'editing': true};
        $scope.items.splice(position, 0, item);
        $scope.updateGallery(true)
    };
    $scope.cancel = function() {
      $scope.editing = false;
    };
    $scope.deleteGallery = function() {
      var confirm = $window.confirm("Are you sure you want to delete this gallery?");
      if (!confirm) {
        return;
      }
      $http.delete("/admin/api/gallery/" + $scope.gallery_uuid).success(function(data) {
          $window.location = "/admin/galleries";
      });
    };
    $scope.unpublishGallery = function() {
        var confirm = $window.confirm("Are you sure you want to unpublish this blog post?");
        if (!confirm) {
            return;
        }
        $scope.published = false;
        $scope.updateGallery(false);
    };
    $scope.publishGallery = function() {
        if (!$scope.coverPhoto) {
            alert("You can't publish a gallery without a cover photo.");
            return;
        }
        var confirm = $window.confirm("Are you sure you want to publish this blog post?");
        if (!confirm) {
            return;
        }
        $scope.published = true;
        $scope.updateGallery(false);
    };
    $scope.sendEmails = function() {
        var confirm = $window.confirm("Are you sure you want to send notification emails for this blog post?");
        if (!confirm) {
            return;
        }
        var $btn = $('.send-emails').button('loading');
        $http.post('/admin/api/gallery/' + $scope.gallery_uuid + '/send_emails').success(function() {
            $btn.button('reset');
        }).error(function(response) {
            alert('Emails failed to send for some reason!')
        });
    }
    $scope.updateItemsPosition = function() {
      var i;
      for (i = 0; i < $scope.items.length; i++) {
          $scope.items[i].position = i + 1;
      }
    };
    $scope.updateGallery = function(updateItems) {
        $scope.updateItemsPosition();
        var data = {'name': $scope.name,
                    'subtitle': $scope.subtitle,
                    'author': $scope.author,
                    'cover_photo': $scope.coverPhoto};
        if ($scope.gallery_uuid) {
            if (updateItems) {
                data['items'] = $scope.items;
            }
            data['published'] = $scope.published;
            $http.put("/admin/api/gallery/" + $scope.gallery_uuid, data).success(function(response) {
                $scope.editing = false;
                $scope.initGallery(response);
            });
        } else {
            data['items'] = $scope.items;
            $http.post("/admin/api/galleries", data).success(function(response) {
                $window.location = "/admin/gallery/" + response.uuid;
            });
        }
    };
    $http.get('/admin/api/categories').success(function(response) {
        $scope.categories = response;
    });
    $scope.currentCategories = function() {
        if (!$scope.gallery || !$scope.categories) {
            return [];
        }
        var current = [];
        var i;
        var inArray;
        for (i = 0; i < $scope.categories.length; i++) {
            inArray = $scope.gallery.gallery_categories.filter(function(obj) {
                return obj.category_uuid == $scope.categories[i].uuid;
            });
            if (inArray.length == 0) {
                current.push($scope.categories[i]);
            }
            inArray = [];
        }
        return current;
    };
    $scope.addCategory = function(category) {
        $http.post('/admin/api/gallery/' + $scope.gallery_uuid + '/categories', data={'category_uuid': category.uuid}).success(function(response) {
            $scope.gallery.gallery_categories = response;
            $scope.newCategory = '';
        });
    };
    $scope.removeCategory = function(category) {
        $http.delete('/admin/api/gallery/' + $scope.gallery_uuid + '/categories/' + category.uuid).success(function(response) {
            $scope.gallery.gallery_categories = response;
            $scope.newCategory = '';
        });
    };
}]);

angularApp.controller('GalleryItemCommentController', ['$scope', '$http', '$window', '$sce', '$upload', '$log', function($scope, $http, $window, $sce, $upload, $log) {
    $scope.newComment = '';
    $scope.showResolved = false;
    $scope.initGalleryItem = function(gallery_item) {
        $scope.galleryItem = gallery_item;
    };
    $scope.resolveComment = function(comment) {
        $http.post('/admin/api/gallery/item/' + $scope.galleryItem.uuid + '/comments/' + comment.uuid, data={'resolved': true}).success(function(response) {
            $scope.galleryItem = response;
        });
    };
    $scope.addComment = function() {
        $http.post('/admin/api/gallery/item/' + $scope.galleryItem.uuid + '/comments', data={'body': $scope.newComment}).success(function(response) {
            $scope.newComment = '';
            $scope.galleryItem = response;
        });
    };
    $scope.currentComments = function() {
        if ($scope.showResolved) {
            return $scope.galleryItem.comments;
        }
        var unresolvedComments = [];
        var comment;
        for (i = 0; i < $scope.galleryItem.comments.length; i++) {
            comment = $scope.galleryItem.comments[i];
            if (!comment.resolved) {
                unresolvedComments.push(comment);
            }
        }
        return unresolvedComments;
    };
    $scope.toggleResolvedComments = function() {
        $scope.showResolved = !$scope.showResolved;
    };
    $scope.showComment = function(comment) {
        if (!comment.resolved) {
            return true;
        }
        if ($scope.showResolved && comment.resolved) {
            return true;
        }
        return false;
    };
    $scope.deleteComment = function(comment) {
        var confirm = $window.confirm("Are you sure you want to delete this comment?");
        if (!confirm) {
            return;
        }
        $http.delete('/admin/api/gallery/item/' + $scope.galleryItem.uuid + '/comments/' + comment.uuid).success(function(response) {
            $scope.galleryItem = response;
        });
    };
}]);

angularApp.controller('GalleryItemController', ['$scope', '$http', '$window', '$sce', '$upload', '$log', function($scope, $http, $window, $sce, $upload, $log) {
    $scope.file = [];
    $scope.dataUrls = [];
    $scope.item = null;
    $scope.error = false;
    $scope.alertMessage = '';
    $scope.loading = false;
    $scope.widthStyle = {"width": "0%"};
    $scope.generatingSizes = false;
    $scope.init = function(imageRoute, item) {
        $scope.imageRoute = imageRoute;
        $scope.item = item;
    };
    $scope.onFileSelect = function($files) {
        $scope.files = $files;
        for (var i = 0; i < $files.length; i++) {
        var file = $files[i];
        var timeStamp = new Date().getTime();
        var fileName = timeStamp + "_" + file.name;
        var fields = fileName.split('\.');
        fileName = fields[0];
        var key = $scope.imageRoute + "/" + fileName;
        var data = {
                key: key,
                AWSAccessKeyId: accessKey, 
                acl: 'public-read',
                policy: policy,
                signature: signature,
                "Content-Type": file.type != '' ? file.type : 'application/octet-stream',
                filename: key,
        };
        $upload.upload({
            url: imagesBase,
            method: 'POST',
            data: data,
            file: file,
        }).progress(function(evt) {
            $scope.percent = parseInt(100.0 * evt.loaded / evt.total);
            $scope.widthStyle = {"width": $scope.percent + "%"};
            $scope.loading = true;
        }).success(function(data, status, headers, config) {
            $scope.generatingSizes = true;
            data = {"image_route": $scope.imageRoute,
                    "filename": fileName};
            $http.post('/images/generate_sizes', data).success(function(data) {
                $scope.generatingSizes = false;
                $scope.item.image_name = fileName;
                $scope.updateGalleryItem();
            });
        }).error(function(data, status, headers, config) {
            $scope.error = true;
            $scope.alertMessage = "There was an error uploading your photo.";
        }).then(function() {
            $scope.loading = false;
        });
        }
    };
    $scope.toggleAlert = function(show) {
        $scope.error = show;
        $scope.alertMessage = '';
    };
    $scope.updateItemPosition = function(newPosition) {
        $scope.item.position = newPosition;
        var currentPosition = $scope.items.indexOf($scope.item);
        $scope.items.splice(currentPosition, 1);
        $scope.items.splice(newPosition - 1, 0, $scope.item);
        $scope.updateGallery(true);
    };
    $scope.updateGalleryItem = function() {
        if (!$scope.item.uuid) {
            $http.post('/admin/api/gallery/item', data=$scope.item).success(function(response) {
                var currentPosition = $scope.items.indexOf($scope.item);
                $scope.items[currentPosition] = response;
                $scope.item.editing = false;
                $scope.item = response;
            });
        } else {
            $http.post('/admin/api/gallery/item/' + $scope.item.uuid, data=$scope.item).success(function(response) {
                var currentPosition = $scope.items.indexOf($scope.item);
                $scope.items[currentPosition] = response;
                $scope.item = response;
                $scope.item.editing = false;
            });
        }
    };
    $scope.killGalleryItem = function(dead) {
        $scope.item.dead = dead;
        $scope.updateGalleryItem();
    };
    $scope.deleteGalleryItem = function() {
        var confirm = $window.confirm("Are you sure you want to delete this item?");
        if (!confirm) {
            return;
        }
        if (!$scope.item.uuid) {
            var currentPosition = $scope.items.indexOf($scope.item);
            $scope.items.splice(currentPosition, 1);
        }
        $http.delete('/admin/api/gallery/item/' + $scope.item.uuid).success(function() {
            var currentPosition = $scope.items.indexOf($scope.item);
            $scope.items.splice(currentPosition, 1);
            $scope.updateGallery(true);
        });
    };
}]);
