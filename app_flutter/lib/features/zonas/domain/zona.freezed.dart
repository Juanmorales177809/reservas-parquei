// GENERATED CODE - DO NOT MODIFY BY HAND
// coverage:ignore-file
// ignore_for_file: type=lint, type=warning, deprecated_member_use, deprecated_member_use_from_same_package
// ignore_for_file: unused_element, deprecated_member_use, deprecated_member_use_from_same_package, use_function_type_syntax_for_parameters, unnecessary_const, avoid_init_to_null, invalid_override_different_default_values_named, prefer_expression_function_bodies, annotate_overrides, invalid_annotation_target, unnecessary_question_mark

part of 'zona.dart';

// **************************************************************************
// FreezedGenerator
// **************************************************************************

// GENERATED CODE - DO NOT MODIFY BY HAND
// dart format off
T _$identity<T>(T value) => value;

/// @nodoc
mixin _$Zona {

 int get id; String get nombre; int get espacioId; String? get descripcion; int? get capacidad; EstadoEntidad get estado; String get createdAt; String get updatedAt; int? get createdBy; int? get updatedBy; List<int> get recursoIds;
/// Create a copy of Zona
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$ZonaCopyWith<Zona> get copyWith => _$ZonaCopyWithImpl<Zona>(this as Zona, _$identity);

  /// Serializes this Zona to a JSON map.
  Map<String, dynamic> toJson();


@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is Zona&&(identical(other.id, id) || other.id == id)&&(identical(other.nombre, nombre) || other.nombre == nombre)&&(identical(other.espacioId, espacioId) || other.espacioId == espacioId)&&(identical(other.descripcion, descripcion) || other.descripcion == descripcion)&&(identical(other.capacidad, capacidad) || other.capacidad == capacidad)&&(identical(other.estado, estado) || other.estado == estado)&&(identical(other.createdAt, createdAt) || other.createdAt == createdAt)&&(identical(other.updatedAt, updatedAt) || other.updatedAt == updatedAt)&&(identical(other.createdBy, createdBy) || other.createdBy == createdBy)&&(identical(other.updatedBy, updatedBy) || other.updatedBy == updatedBy)&&const DeepCollectionEquality().equals(other.recursoIds, recursoIds));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,id,nombre,espacioId,descripcion,capacidad,estado,createdAt,updatedAt,createdBy,updatedBy,const DeepCollectionEquality().hash(recursoIds));

@override
String toString() {
  return 'Zona(id: $id, nombre: $nombre, espacioId: $espacioId, descripcion: $descripcion, capacidad: $capacidad, estado: $estado, createdAt: $createdAt, updatedAt: $updatedAt, createdBy: $createdBy, updatedBy: $updatedBy, recursoIds: $recursoIds)';
}


}

/// @nodoc
abstract mixin class $ZonaCopyWith<$Res>  {
  factory $ZonaCopyWith(Zona value, $Res Function(Zona) _then) = _$ZonaCopyWithImpl;
@useResult
$Res call({
 int id, String nombre, int espacioId, String? descripcion, int? capacidad, EstadoEntidad estado, String createdAt, String updatedAt, int? createdBy, int? updatedBy, List<int> recursoIds
});




}
/// @nodoc
class _$ZonaCopyWithImpl<$Res>
    implements $ZonaCopyWith<$Res> {
  _$ZonaCopyWithImpl(this._self, this._then);

  final Zona _self;
  final $Res Function(Zona) _then;

/// Create a copy of Zona
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? id = null,Object? nombre = null,Object? espacioId = null,Object? descripcion = freezed,Object? capacidad = freezed,Object? estado = null,Object? createdAt = null,Object? updatedAt = null,Object? createdBy = freezed,Object? updatedBy = freezed,Object? recursoIds = null,}) {
  return _then(Zona(
id: null == id ? _self.id : id // ignore: cast_nullable_to_non_nullable
as int,nombre: null == nombre ? _self.nombre : nombre // ignore: cast_nullable_to_non_nullable
as String,espacioId: null == espacioId ? _self.espacioId : espacioId // ignore: cast_nullable_to_non_nullable
as int,descripcion: freezed == descripcion ? _self.descripcion : descripcion // ignore: cast_nullable_to_non_nullable
as String?,capacidad: freezed == capacidad ? _self.capacidad : capacidad // ignore: cast_nullable_to_non_nullable
as int?,estado: null == estado ? _self.estado : estado // ignore: cast_nullable_to_non_nullable
as EstadoEntidad,createdAt: null == createdAt ? _self.createdAt : createdAt // ignore: cast_nullable_to_non_nullable
as String,updatedAt: null == updatedAt ? _self.updatedAt : updatedAt // ignore: cast_nullable_to_non_nullable
as String,createdBy: freezed == createdBy ? _self.createdBy : createdBy // ignore: cast_nullable_to_non_nullable
as int?,updatedBy: freezed == updatedBy ? _self.updatedBy : updatedBy // ignore: cast_nullable_to_non_nullable
as int?,recursoIds: null == recursoIds ? _self.recursoIds : recursoIds // ignore: cast_nullable_to_non_nullable
as List<int>,
  ));
}

}


/// Adds pattern-matching-related methods to [Zona].
extension ZonaPatterns on Zona {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _Zona value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _Zona() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _Zona value)  $default,){
final _that = this;
switch (_that) {
case _Zona():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _Zona value)?  $default,){
final _that = this;
switch (_that) {
case _Zona() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function( int id,  String nombre,  int espacioId,  String? descripcion,  int? capacidad,  EstadoEntidad estado,  String createdAt,  String updatedAt,  int? createdBy,  int? updatedBy,  List<int> recursoIds)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _Zona() when $default != null:
return $default(_that.id,_that.nombre,_that.espacioId,_that.descripcion,_that.capacidad,_that.estado,_that.createdAt,_that.updatedAt,_that.createdBy,_that.updatedBy,_that.recursoIds);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function( int id,  String nombre,  int espacioId,  String? descripcion,  int? capacidad,  EstadoEntidad estado,  String createdAt,  String updatedAt,  int? createdBy,  int? updatedBy,  List<int> recursoIds)  $default,) {final _that = this;
switch (_that) {
case _Zona():
return $default(_that.id,_that.nombre,_that.espacioId,_that.descripcion,_that.capacidad,_that.estado,_that.createdAt,_that.updatedAt,_that.createdBy,_that.updatedBy,_that.recursoIds);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function( int id,  String nombre,  int espacioId,  String? descripcion,  int? capacidad,  EstadoEntidad estado,  String createdAt,  String updatedAt,  int? createdBy,  int? updatedBy,  List<int> recursoIds)?  $default,) {final _that = this;
switch (_that) {
case _Zona() when $default != null:
return $default(_that.id,_that.nombre,_that.espacioId,_that.descripcion,_that.capacidad,_that.estado,_that.createdAt,_that.updatedAt,_that.createdBy,_that.updatedBy,_that.recursoIds);case _:
  return null;

}
}

}

/// @nodoc
@JsonSerializable()

class _Zona implements Zona {
  const _Zona({required this.id, required this.nombre, required this.espacioId, this.descripcion, this.capacidad, required this.estado, required this.createdAt, required this.updatedAt, this.createdBy, this.updatedBy,  List<int> recursoIds = const []}): _recursoIds = recursoIds;
  factory _Zona.fromJson(Map<String, dynamic> json) => _$ZonaFromJson(json);

@override final  int id;
@override final  String nombre;
@override final  int espacioId;
@override final  String? descripcion;
@override final  int? capacidad;
@override final  EstadoEntidad estado;
@override final  String createdAt;
@override final  String updatedAt;
@override final  int? createdBy;
@override final  int? updatedBy;
 final  List<int> _recursoIds;
@override@JsonKey() List<int> get recursoIds {
  if (_recursoIds is EqualUnmodifiableListView) return _recursoIds;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(_recursoIds);
}


/// Create a copy of Zona
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$ZonaCopyWith<_Zona> get copyWith => __$ZonaCopyWithImpl<_Zona>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$ZonaToJson(this, );
}

@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is _Zona&&(identical(other.id, id) || other.id == id)&&(identical(other.nombre, nombre) || other.nombre == nombre)&&(identical(other.espacioId, espacioId) || other.espacioId == espacioId)&&(identical(other.descripcion, descripcion) || other.descripcion == descripcion)&&(identical(other.capacidad, capacidad) || other.capacidad == capacidad)&&(identical(other.estado, estado) || other.estado == estado)&&(identical(other.createdAt, createdAt) || other.createdAt == createdAt)&&(identical(other.updatedAt, updatedAt) || other.updatedAt == updatedAt)&&(identical(other.createdBy, createdBy) || other.createdBy == createdBy)&&(identical(other.updatedBy, updatedBy) || other.updatedBy == updatedBy)&&const DeepCollectionEquality().equals(other._recursoIds, _recursoIds));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,id,nombre,espacioId,descripcion,capacidad,estado,createdAt,updatedAt,createdBy,updatedBy,const DeepCollectionEquality().hash(_recursoIds));

@override
String toString() {
  return 'Zona(id: $id, nombre: $nombre, espacioId: $espacioId, descripcion: $descripcion, capacidad: $capacidad, estado: $estado, createdAt: $createdAt, updatedAt: $updatedAt, createdBy: $createdBy, updatedBy: $updatedBy, recursoIds: $recursoIds)';
}


}

/// @nodoc
abstract mixin class _$ZonaCopyWith<$Res> implements $ZonaCopyWith<$Res> {
  factory _$ZonaCopyWith(_Zona value, $Res Function(_Zona) _then) = __$ZonaCopyWithImpl;
@override @useResult
$Res call({
 int id, String nombre, int espacioId, String? descripcion, int? capacidad, EstadoEntidad estado, String createdAt, String updatedAt, int? createdBy, int? updatedBy, List<int> recursoIds
});




}
/// @nodoc
class __$ZonaCopyWithImpl<$Res>
    implements _$ZonaCopyWith<$Res> {
  __$ZonaCopyWithImpl(this._self, this._then);

  final _Zona _self;
  final $Res Function(_Zona) _then;

/// Create a copy of Zona
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? id = null,Object? nombre = null,Object? espacioId = null,Object? descripcion = freezed,Object? capacidad = freezed,Object? estado = null,Object? createdAt = null,Object? updatedAt = null,Object? createdBy = freezed,Object? updatedBy = freezed,Object? recursoIds = null,}) {
  return _then(_Zona(
id: null == id ? _self.id : id // ignore: cast_nullable_to_non_nullable
as int,nombre: null == nombre ? _self.nombre : nombre // ignore: cast_nullable_to_non_nullable
as String,espacioId: null == espacioId ? _self.espacioId : espacioId // ignore: cast_nullable_to_non_nullable
as int,descripcion: freezed == descripcion ? _self.descripcion : descripcion // ignore: cast_nullable_to_non_nullable
as String?,capacidad: freezed == capacidad ? _self.capacidad : capacidad // ignore: cast_nullable_to_non_nullable
as int?,estado: null == estado ? _self.estado : estado // ignore: cast_nullable_to_non_nullable
as EstadoEntidad,createdAt: null == createdAt ? _self.createdAt : createdAt // ignore: cast_nullable_to_non_nullable
as String,updatedAt: null == updatedAt ? _self.updatedAt : updatedAt // ignore: cast_nullable_to_non_nullable
as String,createdBy: freezed == createdBy ? _self.createdBy : createdBy // ignore: cast_nullable_to_non_nullable
as int?,updatedBy: freezed == updatedBy ? _self.updatedBy : updatedBy // ignore: cast_nullable_to_non_nullable
as int?,recursoIds: null == recursoIds ? _self._recursoIds : recursoIds // ignore: cast_nullable_to_non_nullable
as List<int>,
  ));
}


}

// dart format on
