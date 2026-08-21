// GENERATED CODE - DO NOT MODIFY BY HAND
// coverage:ignore-file
// ignore_for_file: type=lint, type=warning, deprecated_member_use, deprecated_member_use_from_same_package
// ignore_for_file: unused_element, deprecated_member_use, deprecated_member_use_from_same_package, use_function_type_syntax_for_parameters, unnecessary_const, avoid_init_to_null, invalid_override_different_default_values_named, prefer_expression_function_bodies, annotate_overrides, invalid_annotation_target, unnecessary_question_mark

part of 'ensayo.dart';

// **************************************************************************
// FreezedGenerator
// **************************************************************************

// GENERATED CODE - DO NOT MODIFY BY HAND
// dart format off
T _$identity<T>(T value) => value;

/// @nodoc
mixin _$Ensayo {

 int get id; String get nombre; int get zonaId; EstadoEntidad get estado; String get createdAt; String get updatedAt; int get createdBy; int get updatedBy;
/// Create a copy of Ensayo
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$EnsayoCopyWith<Ensayo> get copyWith => _$EnsayoCopyWithImpl<Ensayo>(this as Ensayo, _$identity);

  /// Serializes this Ensayo to a JSON map.
  Map<String, dynamic> toJson();


@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is Ensayo&&(identical(other.id, id) || other.id == id)&&(identical(other.nombre, nombre) || other.nombre == nombre)&&(identical(other.zonaId, zonaId) || other.zonaId == zonaId)&&(identical(other.estado, estado) || other.estado == estado)&&(identical(other.createdAt, createdAt) || other.createdAt == createdAt)&&(identical(other.updatedAt, updatedAt) || other.updatedAt == updatedAt)&&(identical(other.createdBy, createdBy) || other.createdBy == createdBy)&&(identical(other.updatedBy, updatedBy) || other.updatedBy == updatedBy));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,id,nombre,zonaId,estado,createdAt,updatedAt,createdBy,updatedBy);

@override
String toString() {
  return 'Ensayo(id: $id, nombre: $nombre, zonaId: $zonaId, estado: $estado, createdAt: $createdAt, updatedAt: $updatedAt, createdBy: $createdBy, updatedBy: $updatedBy)';
}


}

/// @nodoc
abstract mixin class $EnsayoCopyWith<$Res>  {
  factory $EnsayoCopyWith(Ensayo value, $Res Function(Ensayo) _then) = _$EnsayoCopyWithImpl;
@useResult
$Res call({
 int id, String nombre, int zonaId, EstadoEntidad estado, String createdAt, String updatedAt, int createdBy, int updatedBy
});




}
/// @nodoc
class _$EnsayoCopyWithImpl<$Res>
    implements $EnsayoCopyWith<$Res> {
  _$EnsayoCopyWithImpl(this._self, this._then);

  final Ensayo _self;
  final $Res Function(Ensayo) _then;

/// Create a copy of Ensayo
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? id = null,Object? nombre = null,Object? zonaId = null,Object? estado = null,Object? createdAt = null,Object? updatedAt = null,Object? createdBy = null,Object? updatedBy = null,}) {
  return _then(Ensayo(
id: null == id ? _self.id : id // ignore: cast_nullable_to_non_nullable
as int,nombre: null == nombre ? _self.nombre : nombre // ignore: cast_nullable_to_non_nullable
as String,zonaId: null == zonaId ? _self.zonaId : zonaId // ignore: cast_nullable_to_non_nullable
as int,estado: null == estado ? _self.estado : estado // ignore: cast_nullable_to_non_nullable
as EstadoEntidad,createdAt: null == createdAt ? _self.createdAt : createdAt // ignore: cast_nullable_to_non_nullable
as String,updatedAt: null == updatedAt ? _self.updatedAt : updatedAt // ignore: cast_nullable_to_non_nullable
as String,createdBy: null == createdBy ? _self.createdBy : createdBy // ignore: cast_nullable_to_non_nullable
as int,updatedBy: null == updatedBy ? _self.updatedBy : updatedBy // ignore: cast_nullable_to_non_nullable
as int,
  ));
}

}


/// Adds pattern-matching-related methods to [Ensayo].
extension EnsayoPatterns on Ensayo {
/// A variant of `map` that fallback to returning `orElse`.
///
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case final Subclass value:
///     return ...;
///   case _:
///     return orElse();
/// }
/// ```

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _Ensayo value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _Ensayo() when $default != null:
return $default(_that);case _:
  return orElse();

}
}
/// A `switch`-like method, using callbacks.
///
/// Callbacks receives the raw object, upcasted.
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case final Subclass value:
///     return ...;
///   case final Subclass2 value:
///     return ...;
/// }
/// ```

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _Ensayo value)  $default,){
final _that = this;
switch (_that) {
case _Ensayo():
return $default(_that);case _:
  throw StateError('Unexpected subclass');

}
}
/// A variant of `map` that fallback to returning `null`.
///
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case final Subclass value:
///     return ...;
///   case _:
///     return null;
/// }
/// ```

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _Ensayo value)?  $default,){
final _that = this;
switch (_that) {
case _Ensayo() when $default != null:
return $default(_that);case _:
  return null;

}
}
/// A variant of `when` that fallback to an `orElse` callback.
///
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case Subclass(:final field):
///     return ...;
///   case _:
///     return orElse();
/// }
/// ```

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function( int id,  String nombre,  int zonaId,  EstadoEntidad estado,  String createdAt,  String updatedAt,  int createdBy,  int updatedBy)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _Ensayo() when $default != null:
return $default(_that.id,_that.nombre,_that.zonaId,_that.estado,_that.createdAt,_that.updatedAt,_that.createdBy,_that.updatedBy);case _:
  return orElse();

}
}
/// A `switch`-like method, using callbacks.
///
/// As opposed to `map`, this offers destructuring.
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case Subclass(:final field):
///     return ...;
///   case Subclass2(:final field2):
///     return ...;
/// }
/// ```

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function( int id,  String nombre,  int zonaId,  EstadoEntidad estado,  String createdAt,  String updatedAt,  int createdBy,  int updatedBy)  $default,) {final _that = this;
switch (_that) {
case _Ensayo():
return $default(_that.id,_that.nombre,_that.zonaId,_that.estado,_that.createdAt,_that.updatedAt,_that.createdBy,_that.updatedBy);case _:
  throw StateError('Unexpected subclass');

}
}
/// A variant of `when` that fallback to returning `null`
///
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case Subclass(:final field):
///     return ...;
///   case _:
///     return null;
/// }
/// ```

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function( int id,  String nombre,  int zonaId,  EstadoEntidad estado,  String createdAt,  String updatedAt,  int createdBy,  int updatedBy)?  $default,) {final _that = this;
switch (_that) {
case _Ensayo() when $default != null:
return $default(_that.id,_that.nombre,_that.zonaId,_that.estado,_that.createdAt,_that.updatedAt,_that.createdBy,_that.updatedBy);case _:
  return null;

}
}

}

/// @nodoc
@JsonSerializable()

class _Ensayo implements Ensayo {
  const _Ensayo({required this.id, required this.nombre, required this.zonaId, required this.estado, required this.createdAt, required this.updatedAt, required this.createdBy, required this.updatedBy});
  factory _Ensayo.fromJson(Map<String, dynamic> json) => _$EnsayoFromJson(json);

@override final  int id;
@override final  String nombre;
@override final  int zonaId;
@override final  EstadoEntidad estado;
@override final  String createdAt;
@override final  String updatedAt;
@override final  int createdBy;
@override final  int updatedBy;

/// Create a copy of Ensayo
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$EnsayoCopyWith<_Ensayo> get copyWith => __$EnsayoCopyWithImpl<_Ensayo>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$EnsayoToJson(this, );
}

@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is _Ensayo&&(identical(other.id, id) || other.id == id)&&(identical(other.nombre, nombre) || other.nombre == nombre)&&(identical(other.zonaId, zonaId) || other.zonaId == zonaId)&&(identical(other.estado, estado) || other.estado == estado)&&(identical(other.createdAt, createdAt) || other.createdAt == createdAt)&&(identical(other.updatedAt, updatedAt) || other.updatedAt == updatedAt)&&(identical(other.createdBy, createdBy) || other.createdBy == createdBy)&&(identical(other.updatedBy, updatedBy) || other.updatedBy == updatedBy));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,id,nombre,zonaId,estado,createdAt,updatedAt,createdBy,updatedBy);

@override
String toString() {
  return 'Ensayo(id: $id, nombre: $nombre, zonaId: $zonaId, estado: $estado, createdAt: $createdAt, updatedAt: $updatedAt, createdBy: $createdBy, updatedBy: $updatedBy)';
}


}

/// @nodoc
abstract mixin class _$EnsayoCopyWith<$Res> implements $EnsayoCopyWith<$Res> {
  factory _$EnsayoCopyWith(_Ensayo value, $Res Function(_Ensayo) _then) = __$EnsayoCopyWithImpl;
@override @useResult
$Res call({
 int id, String nombre, int zonaId, EstadoEntidad estado, String createdAt, String updatedAt, int createdBy, int updatedBy
});




}
/// @nodoc
class __$EnsayoCopyWithImpl<$Res>
    implements _$EnsayoCopyWith<$Res> {
  __$EnsayoCopyWithImpl(this._self, this._then);

  final _Ensayo _self;
  final $Res Function(_Ensayo) _then;

/// Create a copy of Ensayo
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? id = null,Object? nombre = null,Object? zonaId = null,Object? estado = null,Object? createdAt = null,Object? updatedAt = null,Object? createdBy = null,Object? updatedBy = null,}) {
  return _then(_Ensayo(
id: null == id ? _self.id : id // ignore: cast_nullable_to_non_nullable
as int,nombre: null == nombre ? _self.nombre : nombre // ignore: cast_nullable_to_non_nullable
as String,zonaId: null == zonaId ? _self.zonaId : zonaId // ignore: cast_nullable_to_non_nullable
as int,estado: null == estado ? _self.estado : estado // ignore: cast_nullable_to_non_nullable
as EstadoEntidad,createdAt: null == createdAt ? _self.createdAt : createdAt // ignore: cast_nullable_to_non_nullable
as String,updatedAt: null == updatedAt ? _self.updatedAt : updatedAt // ignore: cast_nullable_to_non_nullable
as String,createdBy: null == createdBy ? _self.createdBy : createdBy // ignore: cast_nullable_to_non_nullable
as int,updatedBy: null == updatedBy ? _self.updatedBy : updatedBy // ignore: cast_nullable_to_non_nullable
as int,
  ));
}


}

// dart format on
