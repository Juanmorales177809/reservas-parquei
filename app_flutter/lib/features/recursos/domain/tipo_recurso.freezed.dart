// GENERATED CODE - DO NOT MODIFY BY HAND
// coverage:ignore-file
// ignore_for_file: type=lint, type=warning, deprecated_member_use, deprecated_member_use_from_same_package
// ignore_for_file: unused_element, deprecated_member_use, deprecated_member_use_from_same_package, use_function_type_syntax_for_parameters, unnecessary_const, avoid_init_to_null, invalid_override_different_default_values_named, prefer_expression_function_bodies, annotate_overrides, invalid_annotation_target, unnecessary_question_mark

part of 'tipo_recurso.dart';

// **************************************************************************
// FreezedGenerator
// **************************************************************************

// GENERATED CODE - DO NOT MODIFY BY HAND
// dart format off
T _$identity<T>(T value) => value;

/// @nodoc
mixin _$TipoRecurso {

 int get id; String get nombre; String get descripcion; String get activo;
/// Create a copy of TipoRecurso
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$TipoRecursoCopyWith<TipoRecurso> get copyWith => _$TipoRecursoCopyWithImpl<TipoRecurso>(this as TipoRecurso, _$identity);

  /// Serializes this TipoRecurso to a JSON map.
  Map<String, dynamic> toJson();


@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is TipoRecurso&&(identical(other.id, id) || other.id == id)&&(identical(other.nombre, nombre) || other.nombre == nombre)&&(identical(other.descripcion, descripcion) || other.descripcion == descripcion)&&(identical(other.activo, activo) || other.activo == activo));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,id,nombre,descripcion,activo);

@override
String toString() {
  return 'TipoRecurso(id: $id, nombre: $nombre, descripcion: $descripcion, activo: $activo)';
}


}

/// @nodoc
abstract mixin class $TipoRecursoCopyWith<$Res>  {
  factory $TipoRecursoCopyWith(TipoRecurso value, $Res Function(TipoRecurso) _then) = _$TipoRecursoCopyWithImpl;
@useResult
$Res call({
 int id, String nombre, String descripcion, String activo
});




}
/// @nodoc
class _$TipoRecursoCopyWithImpl<$Res>
    implements $TipoRecursoCopyWith<$Res> {
  _$TipoRecursoCopyWithImpl(this._self, this._then);

  final TipoRecurso _self;
  final $Res Function(TipoRecurso) _then;

/// Create a copy of TipoRecurso
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? id = null,Object? nombre = null,Object? descripcion = null,Object? activo = null,}) {
  return _then(TipoRecurso(
id: null == id ? _self.id : id // ignore: cast_nullable_to_non_nullable
as int,nombre: null == nombre ? _self.nombre : nombre // ignore: cast_nullable_to_non_nullable
as String,descripcion: null == descripcion ? _self.descripcion : descripcion // ignore: cast_nullable_to_non_nullable
as String,activo: null == activo ? _self.activo : activo // ignore: cast_nullable_to_non_nullable
as String,
  ));
}

}


/// Adds pattern-matching-related methods to [TipoRecurso].
extension TipoRecursoPatterns on TipoRecurso {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _TipoRecurso value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _TipoRecurso() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _TipoRecurso value)  $default,){
final _that = this;
switch (_that) {
case _TipoRecurso():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _TipoRecurso value)?  $default,){
final _that = this;
switch (_that) {
case _TipoRecurso() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function( int id,  String nombre,  String descripcion,  String activo)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _TipoRecurso() when $default != null:
return $default(_that.id,_that.nombre,_that.descripcion,_that.activo);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function( int id,  String nombre,  String descripcion,  String activo)  $default,) {final _that = this;
switch (_that) {
case _TipoRecurso():
return $default(_that.id,_that.nombre,_that.descripcion,_that.activo);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function( int id,  String nombre,  String descripcion,  String activo)?  $default,) {final _that = this;
switch (_that) {
case _TipoRecurso() when $default != null:
return $default(_that.id,_that.nombre,_that.descripcion,_that.activo);case _:
  return null;

}
}

}

/// @nodoc
@JsonSerializable()

class _TipoRecurso implements TipoRecurso {
  const _TipoRecurso({required this.id, required this.nombre, required this.descripcion, required this.activo});
  factory _TipoRecurso.fromJson(Map<String, dynamic> json) => _$TipoRecursoFromJson(json);

@override final  int id;
@override final  String nombre;
@override final  String descripcion;
@override final  String activo;

/// Create a copy of TipoRecurso
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$TipoRecursoCopyWith<_TipoRecurso> get copyWith => __$TipoRecursoCopyWithImpl<_TipoRecurso>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$TipoRecursoToJson(this, );
}

@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is _TipoRecurso&&(identical(other.id, id) || other.id == id)&&(identical(other.nombre, nombre) || other.nombre == nombre)&&(identical(other.descripcion, descripcion) || other.descripcion == descripcion)&&(identical(other.activo, activo) || other.activo == activo));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,id,nombre,descripcion,activo);

@override
String toString() {
  return 'TipoRecurso(id: $id, nombre: $nombre, descripcion: $descripcion, activo: $activo)';
}


}

/// @nodoc
abstract mixin class _$TipoRecursoCopyWith<$Res> implements $TipoRecursoCopyWith<$Res> {
  factory _$TipoRecursoCopyWith(_TipoRecurso value, $Res Function(_TipoRecurso) _then) = __$TipoRecursoCopyWithImpl;
@override @useResult
$Res call({
 int id, String nombre, String descripcion, String activo
});




}
/// @nodoc
class __$TipoRecursoCopyWithImpl<$Res>
    implements _$TipoRecursoCopyWith<$Res> {
  __$TipoRecursoCopyWithImpl(this._self, this._then);

  final _TipoRecurso _self;
  final $Res Function(_TipoRecurso) _then;

/// Create a copy of TipoRecurso
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? id = null,Object? nombre = null,Object? descripcion = null,Object? activo = null,}) {
  return _then(_TipoRecurso(
id: null == id ? _self.id : id // ignore: cast_nullable_to_non_nullable
as int,nombre: null == nombre ? _self.nombre : nombre // ignore: cast_nullable_to_non_nullable
as String,descripcion: null == descripcion ? _self.descripcion : descripcion // ignore: cast_nullable_to_non_nullable
as String,activo: null == activo ? _self.activo : activo // ignore: cast_nullable_to_non_nullable
as String,
  ));
}


}

// dart format on
